#!/usr/bin/env python2
# Run sanity checks against test database

import unittest

from joern.all import JoernSteps

class PythonJoernTests(unittest.TestCase):
    
    def setUp(self):
        self.j = JoernSteps()
        self.j.connectToDatabase()

    def tearDown(self):
        pass

class IndexLookupTests(PythonJoernTests):
    
    def testGetNodesWithTypeAndCode(self):

        query = 'getNodesWithTypeAndCode("Callee", "bar")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testGetNodesWithTypeAndName(self):

        query = 'getNodesWithTypeAndName("Function", "foo")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
        
    def testGetFunctionsByName(self):
        
        query = 'getFunctionsByName("foo")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testGetCallsTo(self):
        
        query = 'getCallsTo("bar")'
        x = self.j.runGremlinQuery(query)
        self.assertTrue(len(x) == 1)

    def testGetArguments(self):
        
        query = 'getArguments("bar", "0").code'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'y')


class CompositionTests(PythonJoernTests):
    
    def testSyntaxOnlyChaining(self):
        
        # functions calling foo AND bar
        
        query = "getCallsTo('foo').getCallsTo('bar')"
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
    
    def testNotComposition(self):
        
        # functions calling foo AND NOT bar
        
        query = "getCallsTo('foo').not{getCallsTo('bar')}"
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 6)
    
    def testPairsComposition(self):
        
       query = """queryNodeIndex('type:AssignmentExpr AND code:"x = bar ( y )"')
       .pairs( _().lval().code, _().rval().code)"""
       x = self.j.runGremlinQuery(query)
       self.assertEquals(x[0][0], "x")
       self.assertEquals(x[0][1], "bar ( y )")

class UDGTests(PythonJoernTests):
    
    def testComplexArg(self):
        
        query = """getFunctionASTsByName('complexInArgs')
        .astNodes().filter{ it.type == 'Argument'}
        .uses().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 3)

    def testComplexAssign(self):
        
        query = """getFunctionASTsByName('complexAssign')
        .astNodes().filter{ it.type == 'AssignmentExpr'}
        .defines().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'pLtv -> u . u16')


class DataFlowTests(PythonJoernTests):
    
    def testSources(self):
        query = """getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .sources().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testProducers(self):
        query = """ getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .producers(['x'])
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testProducersNegative(self):
        query = """ getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .producers([''])
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 0)

    def testCfgPaths(self):
                
        query = """
        
        dstNode = getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo').statements().toList()[0]

        srcNode = getFunctionASTsByName('ddg_simplest_test')
        .getNodesWithTypeAndCode('AssignmentExpr', '*').statements().toList()[0]
        
        cfgPaths('x', { [] } , srcNode, dstNode )
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x[0]), 2)

    def testUnsanitized(self):
        query = """
        
        getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .unsanitized({[]})
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)


if __name__ == '__main__':
    unittest.main()
    
