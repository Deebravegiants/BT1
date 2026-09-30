# [?] Fix use-after-free bug.

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2021-10-25
Source: https://github.com/argotorg/solidity/commit/dce13fbb6a48c1a62672fa9e057772bafbdf3828
Type: security-commit

## Details
Fix use-after-free bug.

## Patch
### libyul/ControlFlowSideEffectsCollector.cpp
```diff
@@ -212,7 +212,8 @@ ControlFlowSideEffectsCollector::ControlFlowSideEffectsCollector(
 			if (calledSideEffects->canRevert)
 				sideEffects.canRevert = true;
 
-			for (YulString callee: util::valueOrDefault(m_functionCalls, _function))
+			set<YulString> emptySet;
+			for (YulString callee: util::valueOrDefault(m_functionCalls, _function, emptySet))
 				_recurse(callee, _recurse);
 		};
 		for (auto const& call: calls)
```
