# [?] Impose stricter upper bound on memory accesses in order to prevent overflow/wrap around.

## Summary
Severity: Unknown
Chain: Solidity
Component: argotorg/solidity
Published: 2022-01-03
Source: https://github.com/argotorg/solidity/commit/259a98b82c84d40714dc8f250092a572947f014f
Type: security-commit

## Details
Impose stricter upper bound on memory accesses in order to prevent overflow/wrap around.

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
