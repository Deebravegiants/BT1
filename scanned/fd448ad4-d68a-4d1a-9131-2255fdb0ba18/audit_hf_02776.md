# [M] Paused Token Leads to Loss of Funds

## Summary
Severity: Medium
Contest weight: 0.7009
Dataset id: 15173
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the minting or transferring functionality of the wrapped token is paused, the bridging process may fail, resulting in
locked funds. The issue occurs during each call of mint() and transfer().
During bridging, the internal function _receiveToken() is called to finalise the withdrawal. If a lockbox is present, it
first mints the wrapped token to the Bridge contract and then calls withdrawTo() in the lockbox:
```solidity
Bridge.sol
if (_lockbox == address(0)) {
    // If no lockbox is set, just mint the wrapped tokens to the recipient.
    ITokenOps(_token).mint(to, value); // @audit reverts if token is paused
} else {
    // If a lockbox is set, mint the wrapped tokens to the bridge contract.
    ITokenOps(_token).mint(address(this), value); // @audit reverts if token is paused
    // Attempt withdrawal from the lockbox, but transfer the wrapped tokens to the recipient if it fails.
    try ILockbox(_lockbox).withdrawTo(to, value) { } // @audit triggers catch if token is paused
    catch {
        _token.safeTransfer(to, value); // @audit reverts if token is paused
        emit LockboxWithdrawalFailed(_lockbox, to, value);
    }
}
```
When receiveToken() is called on the destination chain, it internally invokes _receiveToken() to mint wrapped to-
kens. The tokens are either sent directly to the recipient or minted to the Bridge contract, depending on whether a
lockbox is present.
However, if the minting functionality in the wrapped token contract is paused, as enforced by
_update()
in
StablecoinUpgradeable.sol then the transaction will revert at lines [271] or [274] in the Bridge contract.
```solidity
StablecoinUpgradeable.sol
function _update(address from, address to, uint256 value)
    internal override(ERC20Upgradeable, ERC20PausableUpgradeable)
    whenAccountNotPaused(from)
    whenAccountNotPaused(to)
    whenAccountNotPaused(_msgSender())
{
    ERC20PausableUpgradeable._update(from, to, value);
}
```
Source: Ripple RLUSD-Implementation
Furthermore, inside the Lockbox, the withdrawTo() function invokes the internal _withdraw() function. This function
first burns the wrapped token from the Bridge using clawback() and then transfers the underlying token to the user:
rlUSD Bridge Contract
```solidity
Lockbox.sol
function _withdraw(address from, address to, uint256 value) internal {
    ITokenOps(wrapped).clawback(from, value);
    token.safeTransfer(to, value);
}
```
If burning is paused in the wrapped token contract, the clawback() function will revert:
```solidity
StablecoinUpgradeable.sol
function _update(address from, address to, uint256 value)
    internal override(ERC20Upgradeable, ERC20PausableUpgradeable)
    whenAccountNotPaused(from)
    whenAccountNotPaused(to)
    whenAccountNotPaused(_msgSender())
{
    ERC20PausableUpgradeable._update(from, to, value);
}
```
Source: Ripple RLUSD-Implementation
As a result, the catch branch in _receiveToken() will be executed to directly transfer the wrapped token to the user.
However, if transferring the wrapped token to to is also paused, it will revert again, causing the withdrawal to fail.
Since the bridging transaction in OmniPortal is non-retryable, this failure results in locked funds.
Due to the non-retriable design of
OmniPortal, this revert does not roll back the entire
xsubmit() transaction in
OmniPortal. As a result, the withdrawal process fails, and the locked tokens become unrecoverable, while the bridging
is considered as successful.

## Recommendation
A solution for the calls to
mint() reverting is to handle such cases using a try-catch mechanism and implement a
retrieval process, allowing users to claim their tokens later.
```solidity
if (_lockbox == address(0)) {
    // If no lockbox is set, just mint the wrapped tokens to the recipient.
    try ITokenOps(_token).mint(to, value) {}
    catch {
        failed[to] += value;
    }
} else {
    // If a lockbox is set, mint the wrapped tokens to the bridge contract.
    try ITokenOps(_token).mint(address(this), value) {}
    catch {
        failed[to] += value;
        return;
    }
}
```
Additionally, for the transfer() calls, should be tracked when a fail occurs across all branches and implement a retry
mechanism, allowing users to claim their funds later. However, consideration must be taken for non-standard ERC20
token implementations as they may not have returndata or return false rather than reverting if a transfer fails.
These approaches ensure that failed withdrawals are properly tracked, allowing users to later reclaim their tokens when
the issue is resolved.
rlUSD Bridge Contract
