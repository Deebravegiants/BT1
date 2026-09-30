# [M] Bypass `whenNotPaused` modifier

## Summary
Severity: Medium
Contest weight: 0.6343
Dataset id: 17262
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an inconsistent application of the emergency‑stop mechanism that is implemented through the whenNotPaused modifier. The contract is designed to block creation of new minipools, staking of GGP tokens and withdrawal of GGP when the admin calls pause(). The pause flag is checked only in functions that are explicitly marked with whenNotPaused, such as stakeGGP() and withdrawGGP(). However, other external entry points – notably restakeGGP() in the Staking contract, claimAndRestake() in the ClaimNodeOp contract and the guardian‑only spend() function – do not include the pause guard. Because these functions are not protected, they can still be invoked while the system is paused, allowing token transfers to and from the vault and additional staking actions. The root cause is a missing whenNotPaused check on functions that move funds, combined with reliance on other modifiers (onlySpecificRegisteredContract, onlyGuardian) that do not consider the paused state. An attacker or any user who can call claimAndRestake can trigger a sequence where the contract withdraws GGP from the vault, optionally restakes it via restakeGGP, and then forwards a claim amount to the caller, all while the protocol is supposed to be in a halted state. This bypass defeats the intended admin control, potentially enabling unintended token movement, reward manipulation, or draining of the vault if the caller is able to repeatedly claim and restake. The issue manifests only when the pause flag is active; under normal operation the functions behave as expected, which makes the bug easy to miss in routine testing that focuses on the primary stake and withdraw functions. It was discovered during a manual audit that compared the presence of the whenNotPaused modifier across related functions and identified the inconsistency. From a user’s perspective the UI may display “paused” while the user can still submit a claim or restake transaction, leading to confusion because the expected behavior is that all token‑moving actions are blocked. This class of bug falls under inconsistent access‑control or emergency‑stop bypass, where some code paths unintentionally ignore the global pause state. The recommended remediation is to add the whenNotPaused modifier to restakeGGP(), claimAndRestake() and, if appropriate, to the spend() function, ensuring that every external function that can transfer tokens respects the paused flag and restores a uniform security posture.

## Proof of Concept
**`stake()`**

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

**`withdraw()`**

In paused mode, no more `withdrawGGP()` is allowed,
    
```solidity
File: contract/Staking.sol
358: 	function withdrawGGP(uint256 amount) external whenNotPaused {

373: 		vault.withdrawToken(msg.sender, ggp, amount);
```

However, `claimAndRestake()` is still available, which can withdraw from the vault.
    
```solidity
File: contract/ClaimNodeOp.sol
089: 	function claimAndRestake(uint256 claimAmt) external {

103: 		if (restakeAmt > 0) {
104: 			vault.withdrawToken(address(this), ggp, restakeAmt);
105: 			ggp.approve(address(staking), restakeAmt);
106: 			staking.restakeGGP(msg.sender, restakeAmt);
107: 		}
108: 
109: 		if (claimAmt > 0) {
110: 			vault.withdrawToken(msg.sender, ggp, claimAmt);
111: 		}
```

The function `spend()` can also ignore the pause mode to withdraw from the vault. But this is a guardian function. It could be intended behavior.
    
```solidity
File: contract/ClaimProtocolDAO.sol
20: 	function spend(
21: 		string memory invoiceID,
22: 		address recipientAddress,
23: 		uint256 amount
24: 	) external onlyGuardian {

32: 		vault.withdrawToken(recipientAddress, ggpToken, amount);
```

## Recommendation
* add the `whenNotPaused` modifier to `restakeGGP()` and `claimAndRestake()`
  * maybe also for guardian function `spend()`.

The warden has shown an inconsistency within similar functions regarding how they behave during a pause.  
Because the finding pertains to an inconsistent functionality, without a loss of principal, I agree with Medium Severity.

Pause claimAndRestake as well: [multisig-labs/gogopool#22](https://github.com/multisig-labs/gogopool/pull/22)
