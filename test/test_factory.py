import unittest

from test_context import *

import hadoop_pipes


class Mapper(hadoop_pipes.Mapper):
  def __init__(self, task_ctx):
    hadoop_pipes.Mapper.__init__(self)
    print 'Mapper has been instantiated'
  def map(self, map_ctx):
    print 'Mapper.map has been invoked'
    k = map_ctx.getInputKey()
    v = map_ctx.getInputValue()
    print 'Mapper.map InputKey=%s'   % k
    print 'Mapper.map InputValue=%s' % v
    map_ctx.emit(k, v)

class Reducer(hadoop_pipes.Reducer):
  def __init__(self, task_ctx):
    hadoop_pipes.Reducer.__init__(self)
    print 'Reducer has been instantiated'
  def reduce(self, map_ctx):
    print 'Reducer.reduce has been invoked'

class Factory(hadoop_pipes.Factory):
  def __init__(self, mapper_class, reducer_class):
    hadoop_pipes.Factory.__init__(self)
    self.mapper_class  = mapper_class
    self.reducer_class = reducer_class
    self.produced      = []

  def createMapper(self, ctx):
    print '--createMapper() Factory.createMapper'
    o = self.mapper_class(ctx)
    print '--createMapper() Factory.createMapper: %r' % o
    self.produced.append(o)
    print '--createMapper() Factory.createMapper: ready to return'
    return o

  def createReducer(self, ctx):
    o = self.reducer_class(ctx)
    self.produced.append(o)
    return o

if __name__ == '__main__' :
  j = jc(jc_fields)
  fact = Factory(Mapper, Reducer)
  mctx = mc(j)
  rctx = rc(j)
  m    = fact.createMapper(mctx)
  m.map(mctx)
  r    = fact.createReducer(rctx)
  r.reduce(rctx)
  test_factory = hadoop_pipes.TestFactory(fact)
  print test_factory
  m = test_factory.createMapper(mctx)
  m.map(mctx)
  r = test_factory.createReducer(rctx)
  r.reduce(rctx)
  hadoop_pipes.try_reducer(r, rctx)
  hadoop_pipes.try_mapper(m, mctx)
  hadoop_pipes.try_factory(fact, mctx, rctx)
  hadoop_pipes.try_factory_internal(fact)


  #hadoop_pipes.runTask(fact)











