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

_Trimmed to 38 lines — full report: https://notes.ethereum.org/zOAIzbDeSvWXuCw7bnEocw_
