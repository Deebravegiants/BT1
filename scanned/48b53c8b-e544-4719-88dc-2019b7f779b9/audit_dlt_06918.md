# [M] Bypass `whenNotPaused` modifier

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-12-gogopool
Published: 2023-01-03
Source: https://github.com/code-423n4/2022-12-gogopool-findings/issues/673
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-12-gogopool/blob/aec9928d8bdce8a5a4efe45f54c39d4fc7313731/contracts/contract/Staking.sol#L328-L332
https://github.com/code-423n4/2022-12-gogopool/blob/aec9928d8bdce8a5a4efe45f54c39d4fc7313731/contracts/contract/ClaimNodeOp.sol#L89-L114
https://github.com/code-423n4/2022-12-gogopool/blob/aec9928d8bdce8a5a4efe45f54c39d4fc7313731/contracts/contract/ClaimProtocolDAO.sol#L20-L35


# Vulnerability details

## Impact

The `whenNotPaused` modifier is used to pause minipool creation and staking/withdrawing GGP. However, there are several cases this modifier could be bypassed, which breaks the intended admin control function and special mode.


## Proof of Concept

### `stake()`

In paused mode, no more `stakeGGP()` is allowed, 
```solidity
File: contract/Staking.sol
319: 	function stakeGGP(uint256 amount) external whenNotPaused {
320: 		// Transfer GGP tokens from staker to this contract
321: 		ggp.safeTransferFrom(msg.sender, address(this), amount);
322: 		_stakeGGP(msg.sender, amount);
323: 	}
```

However, `restakeGGP()` is still available, which potentially violate the purpose of pause mode.
```solidity
File: contract/Staking.sol
328: 	function restakeGGP(address stakerAddr, uint256 amount) public onlySpecificRegisteredContract("ClaimNodeOp", msg.sender) {
329: 		// Transfer GGP tokens from the ClaimNodeOp contract to this contract
330: 		ggp.safeTransferFrom(msg.sender, address(this), amount);
331: 		_stakeGGP(stakerAddr, amount);
332: 	}
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-12-gogopool-findings/issues/673_
