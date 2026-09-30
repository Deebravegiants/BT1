# [?] Merge pull request #377 from crytic/dev-fix-reentrancy-events

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-12-09
Source: https://github.com/crytic/slither/commit/de0f437f0f5abfbf3b51bbeb60853bbd221be067
Type: security-commit

## Details
Merge pull request #377 from crytic/dev-fix-reentrancy-events

Remove FPs in reentrancy-events

## Patch
### scripts/tests_generate_expected_json_5.sh
```diff
@@ -27,6 +27,7 @@ generate_expected_json(){
 #generate_expected_json tests/backdoor.sol "suicidal"
 #generate_expected_json tests/old_solc.sol.json "solc-version"
 #generate_expected_json tests/reentrancy-0.5.1.sol "reentrancy-eth"
+generate_expected_json tests/reentrancy-0.5.1-events.sol "reentrancy-events"
 #generate_expected_json tests/tx_origin-0.5.1.sol "tx-origin"
 #generate_expected_json tests/locked_ether-0.5.1.sol "locked-ether"
 #generate_expected_json tests/arbitrary_send-0.5.1.sol "arbitrary-send"
```

### scripts/travis_test_5.sh
```diff
@@ -78,6 +78,7 @@ test_slither tests/backdoor.sol "backdoor"
 test_slither tests/backdoor.sol "suicidal"
 test_slither tests/old_solc.sol.json "solc-version"
 test_slither tests/reentrancy-0.5.1.sol "reentrancy-eth"
+test_slither tests/reentrancy-0.5.1-events.sol "reentrancy-events"
 test_slither tests/tx_origin-0.5.1.sol "tx-origin"
 test_slither tests/unused_state.sol "unused-state"
 test_slither tests/locked_ether-0.5.1.sol "locked-ether"
```

### scripts/travis_test_etherscan.sh
```diff
@@ -18,7 +18,7 @@ fi
 
 slither rinkeby:0xFe05820C5A92D9bc906D4A46F662dbeba794d3b7 --solc "./solc-0.4.25"
 
-if [ $? -ne 71 ]
+if [ $? -ne 70 ]
 then
     echo "Etherscan test failed"
     exit -1
```

### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -87,7 +87,7 @@ def _explore(self, node, visited, skip_father=None):
         # calls returns the list of calls that can callback
         # read returns the variable read
         # read_prior_calls returns the variable read prior a call
-        fathers_context = {'send_eth': set(), 'calls': set(), 'read': set(), 'read_prior_calls': {}, 'events': set()}
+        fathers_context = {'send_eth': set(), 'calls': set(), 'read': set(), 'read_prior_calls': {}}
 
         for father in node.fathers:
             if self.KEY in father.context:
@@ -97,7 +97,6 @@ def _explore(self, node, visited, skip_father=None):
                 fathers_context['read'] |= set(father.context[self.KEY]['read'])
                 fathers_context['read_prior_calls'] = union_dict(fathers_context['read_prior_calls'],
                                                                  father.context[self.KEY]['read_prior_calls'])
-                fathers_context['events'] |= set(father.context[self.KEY]['events'])
 
         # Exclude path that dont bring further information
         if node in self.visited_all_paths:
@@ -106,8 +105,7 @@ def _explore(self, node, visited, skip_father=None):
                     if fathers_context['read'].issubset(self.visited_all_paths[node]['read']):
                         if dict_are_equal(self.visited_all_paths[node]['read_prior_calls'],
                                           fathers_context['read_prior_calls']):
-                            if fathers_context['events'].issubset(self.visited_all_paths[node]['events']):
-                                return
+                            return
         else:
             self.visited_all_paths[node] = {'send_eth': set(), 'calls': set(), 'read': set(),
                                             'read_prior_calls': {}, 'events': set()}
@@ -117,7 +115,6 @@ def _explore(self, node, visited, skip_father=None):
         self.visited_all_paths[node]['read'] |= fathers_context['read']
         self.visited_all_paths[node]['read_prior_calls'] = union_dict(self.visited_all_paths[node]['read_prior_calls'],
                                                                       fathers_context['read_prior_calls'])
-        self.visited_all_paths[node]['events'] |= fathers_context['events']
 
         node.context[self.KEY] = fathers_context
 
@@ -147,7 +144,7 @@ def _explore(self, node, visited, skip_father=None):
 
         node.context[self.KEY]['read'] |= state_vars_read
 
-        node.context[self.KEY]['events'] |= set([ir for ir in node.irs if isinstance(ir, EventCall)])
+        node.context[self.KEY]['events'] = set([ir for ir in node.irs if isinstance(ir, EventCall)])
 
         sons = node.sons
         if contains_call and node.type in [NodeType.IF, NodeType.IFLOOP]:
```

### tests/expected_json/reentrancy-0.5.1-events.reentrancy-events.json
```diff
@@ -0,0 +1,151 @@
+{
+  "success": true,
+  "error": null,
+  "results": {
+    "detectors": [
+      {
+        "elements": [
+          {
+            "type": "function",
+            "name": "bug",
+            "source_mapping": {
+              "start": 86,
+              "length": 68,
+              "filename_used": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+              "filename_relative": "tests/reentrancy-0.5.1-events.sol",
+              "filename_absolute": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+              "filename_short": "tests/reentrancy-0.5.1-events.sol",
+              "is_dependency": false,
+              "lines": [
+                14,
+                15,
+                16,
+                17
+              ],
+              "starting_column": 5,
+              "ending_column": 6
+            },
+            "type_specific_fields": {
+              "parent": {
+                "type": "contract",
+                "name": "Test",
+                "source_mapping": {
+                  "start": 51,
+                  "length": 193,
+                  "filename_used": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                  "filename_relative": "tests/reentrancy-0.5.1-events.sol",
+                  "filename_absolute": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                  "filename_short": "tests/reentrancy-0.5.1-events.sol",
+                  "is_dependency": false,
+                  "lines": [
+                    11,
+                    12,
+                    13,
+                    14,
+                    15,
+                    16,
+                    17,
+                    18,
+                    19,
+                    20,
+                    21,
+                    22,
+                    23,
+                    24
+                  ],
+                  "starting_column": 1,
+                  "ending_column": 2
+                }
+              },
+              "signature": "bug(C)"
+            }
+          },
+          {
+            "type": "node",
+            "name": "c.f()",
+            "source_mapping": {
+              "start": 120,
+              "length": 5,
+              "filename_used": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+              "filename_relative": "tests/reentrancy-0.5.1-events.sol",
+              "filename_absolute": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+              "filename_short": "tests/reentrancy-0.5.1-events.sol",
+              "is_dependency": false,
+              "lines": [
+                15
+              ],
+              "starting_column": 9,
+              "ending_column": 14
+            },
+            "type_specific_fields": {
+              "parent": {
+                "type": "function",
+                "name": "bug",
+                "source_mapping": {
+                  "start": 86,
+                  "length": 68,
+                  "filename_used": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                  "filename_relative": "tests/reentrancy-0.5.1-events.sol",
+                  "filename_absolute": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                  "filename_short": "tests/reentrancy-0.5.1-events.sol",
+                  "is_dependency": false,
+                  "lines": [
+                    14,
+                    15,
+                    16,
+                    17
+                  ],
+                  "starting_column": 5,
+                  "ending_column": 6
+                },
+                "type_specific_fields": {
+                  "parent": {
+                    "type": "contract",
+                    "name": "Test",
+                    "source_mapping": {
+                      "start": 51,
+                      "length": 193,
+                      "filename_used": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                      "filename_relative": "tests/reentrancy-0.5.1-events.sol",
+                      "filename_absolute": "/home/travis/build/crytic/slither/tests/reentrancy-0.5.1-events.sol",
+                      "filename_short": "tests/reentrancy-0.5.1-events.sol",
+                      "is_dependency": false,
+                      "lines": [
+                        11,
+                        12,
+                        13,
+                        14,
+                        15,
+                        16,
+                        17,
+                        18,
+                        19,
+                        20,
+                        21,
+                        22,
+                        23,
+                        24
+                      ],
+                      "starting_column": 1,
+                      "ending_column": 2
+                    }
+                  },
+                  "signature": "bug(C)"
+                }
+              }
+            },
+            "additional_fields": {
+              "underlying_type": "external_calls"
+            }
+          }
+        ],
+        "description": "Reentrancy in Test.bug(C) (tests/reentrancy-0.5.1-events.sol#14-17):\n\tExternal calls:\n\t- c.f() (tests/reentrancy-0.5.1-events.sol#15)\n\tEvent emitted after the call(s):\n\t- E() (tests/reentrancy-0.5.1-events.sol#16)\n",
+        "markdown": "Reentrancy in [Test.bug(C)](tests/reentrancy-0.5.1-events.sol#L14-L17):\n\tExternal calls:\n\t- [c.f()](tests/reentrancy-0.5.1-events.sol#L15)\n\tEvent emitted after the call(s):\n\t- [E()](tests/reentrancy-0.5.1-events.sol#L16)\n",
+        "id": "9654da7d8b8d85c90bc2ee1ddaea365f98f14d9981149b354f8a3d84f98ea576",
+        "check": "reentrancy-events",
+        "impact": "Low",
+        "confidence": "Medium"
+      }
+    ]
+  }
+}
\ No newline at end of file
```

### tests/expected_json/reentrancy-0.5.1-events.reentrancy-events.txt
```diff
@@ -0,0 +1,9 @@
+[92m
+Reentrancy in Test.bug(C) (tests/reentrancy-0.5.1-events.sol#14-17):
+	External calls:
+	- c.f() (tests/reentrancy-0.5.1-events.sol#15)
+	Event emitted after the call(s):
+	- E() (tests/reentrancy-0.5.1-events.sol#16)
+Reference: https://github.com/crytic/slither/wiki/Detector-Documentation#reentrancy-vulnerabilities-3[0m
+tests/reentrancy-0.5.1-events.sol analyzed (2 contracts with 1 detectors), 1 result(s) found
+[94mUse https://crytic.io/ to get access to additional detectors and Github integration[0m
```

### tests/reentrancy-0.5.1-events.sol
```diff
@@ -0,0 +1,24 @@
+contract C{
+
+
+    function f() public{
+
+    }
+
+}
+
+
+contract Test{
+    event E();
+
+    function bug(C c) public{
+        c.f();
+        emit E();    
+    }
+
+    function ok(C c) public{
+        emit E();    
+        c.f();
+        c.f();
+    }
+}
```
