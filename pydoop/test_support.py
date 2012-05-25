# BEGIN_COPYRIGHT
# 
# Copyright 2012 CRS4.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# 
# END_COPYRIGHT

"""
Miscellaneous utilities for testing.
"""

import sys, os, uuid
import hdfs


def inject_code(new_code, target_code):
  new_code = "{0}#---AUTO-INJECTED---{0}{1}{0}#-------------------{0}".format(
    os.linesep, os.linesep.join(new_code.strip().splitlines())
    )
  if target_code.startswith("#!"):
    target_code = target_code.splitlines()
    target_code[1:1] = [new_code]
    target_code = os.linesep.join(target_code)
  else:
    target_code = new_code + target_code
  return target_code


def add_sys_path(target_code):
  new_code = os.linesep.join([
    "import sys",
    "sys.path = %r" % (sys.path,)
    ])
  return inject_code(new_code, target_code)


def make_random_str(prefix="pydoop_test_"):
  return "%s%s" % (prefix, uuid.uuid4().hex)


def collect_output(mr_out_dir):
  output = []
  for fn in hdfs.ls(mr_out_dir):
    if hdfs.path.basename(fn).startswith("part"):
      with hdfs.open(fn) as f:
        output.append(f.read())
  return "".join(output)


def parse_mr_output(output, vtype=str):
  wc = {}
  for line in output.splitlines():
    if line.isspace():
      continue
    try:
      w, c = line.split()
      c = vtype(c)
    except (ValueError, TypeError):
      raise ValueError("bad output format")
    wc[w] = c
  return wc


def compare_counts(c1, c2):
  if len(c1) != len(c2):
    print len(c1), len(c2)
    return "number of keys differs"
  keys = sorted(c1)
  if sorted(c2) != keys:
    return "key lists are different"
  for k in keys:
    if c1[k] != c2[k]:
      return "values are different for key %r (%r != %r)" % (k, c1[k], c2[k])


class LocalWordCount(object):

  def __init__(self, input_dir, min_occurrence=0):
    self.input_dir = input_dir
    self.min_occurrence = min_occurrence
    self.__expected_output = None

  @property
  def expected_output(self):
    if self.__expected_output is None:
      self.__expected_output = self.run()
    return self.__expected_output

  def run(self):
    wc = {}
    for fn in os.listdir(self.input_dir):
      if fn[0] == ".":
        continue
      with open(os.path.join(self.input_dir, fn)) as f:
        for line in f:
          line = line.split()
          for w in line:
            wc[w] = wc.get(w, 0) + 1
    if self.min_occurrence:
      wc = dict(t for t in wc.iteritems() if t[1] >= self.min_occurrence)
    return wc

  def check(self, output):
    res = compare_counts(
      parse_mr_output(output, vtype=int), self.expected_output
      )
    if res:
      return "ERROR: %s" % res
    else:
      return "OK."
