# [H] Completebypass of transfer restrictions on vault share token is possible

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23350
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In `AccountableVault.sol` (which is inherited by the `AccountableAsyncRedeemVault`), we have certain transfer restrictions (KYC, if from address is subject to a throttle timestamp), applied in `_checkTransfer()` function.  
These restrictions are applied on `transfer()`/ `transferFrom()` function (inherited from ERC20) when share holders try to move their holdings.  
These restrictions do not apply when the internal `_transfer()` function is used, which is fine for most cases as these share tokens will be moved only for deposits and redeems.  

But there is one case where user can use the `cancelRedeemRequest()` feature to bypass all these restrictions completely, and move share tokens to a different address.  
This is how it can be done :

- Assume controller has a deposit in the vault  
- Controller places a redeem request  
- Controller immediately cancels the redeem request  
- Controller calls `claimCancelRedeemRequest()` where share tokens are transferred to a "receiver" address  

```solidity
function claimCancelRedeemRequest(uint256 requestId, address receiver, address controller)
    public
    onlyAuth
    returns (uint256 shares)
{
    _checkController(controller);
    VaultState storage state = _vaultStates[controller];
    shares = state.claimableCancelRedeemRequest;
    if (shares == 0) revert ZeroAmount();
    strategy.onClaimCancelRedeemRequest(address(this), controller);
    state.claimableCancelRedeemRequest = 0;
    _transfer(address(this), receiver, shares); // @audit bypasses all transfer restrictions.
    emit CancelRedeemClaim(receiver, controller, requestId, msg.sender, shares);
}
```

For this transfer step, the internal `_transfer()` function is used which skips all transfer restrictions applicable as per `AccountableVault` logic.  

Impact: This "receiver" address input while calling `claimCancelRedeemRequest()` is the controller's choice and there are no checks on it as `_checkTransfer()` gets bypassed. This allows to transfer shares even if "to" address is not KYC‑ed or transfers originating at "from" address had to work with a cooldown time. This way controller is able to move their vault shares to a random receiver address, bypassing the transfer restrictions.

## Recommendation
In `claimCancelRedeemRequest()`, remove the receiver address logic and just transfer the cancelled shares back to the controller address. This solves the issue as controller is already expected to be KYC‑ed, and there will be no need for a cooldown check in that case as shares are going back to the original holder.
