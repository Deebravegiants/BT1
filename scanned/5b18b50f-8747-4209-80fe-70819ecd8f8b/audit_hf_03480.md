# [H] `_requireVaultCollateralized`

## Summary
Severity: High
Contest weight: 0.7501
Dataset id: 18998
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an invariant‑check ordering flaw in the vault contract. The internal function that verifies a vault remains sufficiently collateralized, _requireVaultCollateralized(), is invoked at the start of the mintYieldFee() and liquidate() functions. Both of these functions subsequently modify the vault’s state – mintYieldFee() increases the protocol’s fee share balance and liquidate() reduces the vault’s collateral or increases its debt. Because the collateralization check runs before these state changes, the contract does not guarantee that the vault is still safe after the operation completes. An attacker can call either function with parameters that push the vault’s collateral‑to‑debt ratio below the required threshold, causing the vault to become under‑collateralized without triggering a revert. This can lead to unintended liquidations, loss of user funds, or the minting of yield fees that exceed the actual value of the underlying assets. The issue manifests whenever mintYieldFee() or liquidate() are executed with values that reduce collateral or increase obligations, which is a common scenario in normal protocol operation. All vault owners and participants are affected because the safety guarantees of the vault are broken, potentially resulting in missing balances, zeroed refunds, or unexpected fee allocations. The problem was discovered during a Code4rena audit through logical analysis of the function flow rather than through a failing test case, making it subtle: the transaction succeeds, no error is emitted, yet the vault’s accounting is compromised. Detecting the bug is difficult because the contract does not emit an event or revert when the vault becomes unsafe after the function finishes; the invariant is only checked at the beginning, giving a false sense of security. The correct mitigation is to move the collateralization verification to the end of each function, or to perform an additional check after the state‑changing operations, ensuring that the vault’s collateralization ratio is still satisfied before the transaction is finalized. Conceptually, this belongs to the class of “post‑condition invariant violation” bugs where safety checks are placed before mutable operations, allowing the system to enter an invalid state after execution. From a user’s perspective, the symptoms may appear as a vault that can be liquidated despite having sufficient collateral before the call, or as a situation where a user expects a fee to be minted based on their share but receives an incorrect amount, effectively causing funds to disappear or be allocated incorrectly.

## Proof of Concept
`_requireVaultCollateralized()` is called at the beginning of `mintYieldFee()` and `liquidate()`. These two functions change the state and the vault could become under-collateralized at the end of the functions.
```solidity
function mintYieldFee(uint256 _shares, address _recipient) external {
    _requireVaultCollateralized();
    if (_shares > _yieldFeeTotalSupply) revert YieldFeeGTAvailable(_shares, _yieldFeeTotalSupply);
```
```solidity
function mintYieldFee(uint256 _shares, address _recipient) external {
    _requireVaultCollateralized();
    if (_shares > _yieldFeeTotalSupply) revert YieldFeeGTAvailable(_shares, _yieldFeeTotalSupply);
```

## Recommendation
Call `_requireVaultCollateralized()` at the end of these functions instead of calling it at the beginning.
