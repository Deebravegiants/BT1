# [?] Merge pull request #12484 from ethereum/fix-interpreter-mem-overflow-bug

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2022-01-03
Source: https://github.com/argotorg/solidity/commit/c28f85f1e2e4403528341472416f510e90f2b1f4
Type: security-commit

## Details
Merge pull request #12484 from ethereum/fix-interpreter-mem-overflow-bug

Impose stricter upper bound on memory accesses in order to prevent wrap around

## Patch
### test/tools/yulInterpreter/EVMInstructionInterpreter.cpp
```diff
@@ -476,7 +476,9 @@ bool EVMInstructionInterpreter::accessMemory(u256 const& _offset, u256 const& _s
 	{
 		u256 newSize = (_offset + _size + 0x1f) & ~u256(0x1f);
 		m_state.msize = max(m_state.msize, newSize);
-		return _size <= 0xffff;
+		// We only record accesses to contiguous memory chunks that are at most 0xffff bytes
+		// in size and at an offset of at most numeric_limits<size_t>::max() - 0xffff
+		return _size <= 0xffff && _offset <= u256(numeric_limits<size_t>::max() - 0xffff);
 	}
 	else
 		m_state.msize = u256(-1);
```
