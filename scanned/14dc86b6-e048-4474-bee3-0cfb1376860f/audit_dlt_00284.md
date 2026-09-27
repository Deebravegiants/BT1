# [M] EL-2022-05: The solidity optimizer incorrectly removes memory writes that affect global state

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Solidity
Published: 2023-05-03
Source: https://notes.ethereum.org/zOAIzbDeSvWXuCw7bnEocw
Type: ef-disclosure

## Details
# The solidity optimizer incorrectly removes memory writes that affect global state

Short description
*
1 sentence description of the bug
The solidity optimizer incorrectly removes memory writes that affect global state
Attack scenario
*
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
When inlining an internal function, the solidity optimizer (apparently) optimizes out mstore commands specified within assembly blocks, despite these mstore commands being observed by later log0/log1/... commands.
Impact
*
 Describe the effect this may have in a production setting
The immutable blockchain ledger will be irrevocably corrupted: log messages will not contain the contents that the developer intends
Components
*
Point to the files, functions, and/or specific line numbers where the bug occurs
I tried to trace down exactly where this optimization was occurring; I was not familiar enough. I assume it has something to do with log* instructions not consuming memory write side effects in the compiler's abstract semantics.
Reproduction
*
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
contract Test {
	uint256 x;
                
	function test() public returns (uint256) {
		uint256 a = myGetX();
		x = 5;
		uint256 b = myGetX();
		assembly {
			log0(0, 64)
		}
		return a + b + myGetX();
	}
                
	function myGetX() internal view returns (uint256) {
		assembly {
			mstore(1, 0x123456789abcdef)
		}
		return x;
	}
}

Compiling this contract with optimizations under solc8.14 will yield bytecode that does not contain the write of 0x123456789abcdef (or even the push of this constant). Alternatively, you can run this contract with/without optimizations against a test ganache client and observe the log contents.
Fix
Description of suggested fix, if available
Details
Any details not covered above
Running the above contract on a test ganache instance, WITHOUT optimizations yields the log payload:
{
  data: '0x000000000000000000000000000000000000000000000000000123456789abcdef00000000000000000000000000000000000000000000000000000000000000',
  topics: []
}
Whereas with optimizations enabled:
{
  data: '0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
  topics: []
}
