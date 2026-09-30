# [?] Fix FPs in reentrancy-events

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2019-11-25
Source: https://github.com/crytic/slither/commit/1d067def92223ac4322e1453b8a1db1bb0918011
Type: security-commit

## Details
Fix FPs in reentrancy-events

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
