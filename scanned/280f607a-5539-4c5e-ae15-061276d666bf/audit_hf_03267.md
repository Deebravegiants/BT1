# [M] WithdrawProxy allows `redeem

## Summary
Severity: Medium
Contest weight: 0.4688
Dataset id: 17921
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WithdrawProxy contract has the `onlyWhenNoActiveAuction` modifier on the `withdraw()` and `redeem()` functions. This modifier stops these functions from being called when an auction is active:

```solidity
modifier onlyWhenNoActiveAuction() {
  WPStorage storage s = _loadSlot();
  if (s.finalAuctionEnd != 0) {
    revert InvalidState(InvalidStates.NOT_CLAIMED);
  }
  _;
}
```

Furthermore, both `withdraw()` and `redeem()` can only be called when `totalAssets() > 0` based on logic within those functions.

The intention of these two checks is that the WithdrawProxy shares can only be cashed out after the PublicVault has called `transferWithdrawReserve`.

However, because `s.finalAuctionEnd == 0` before an auction has started, and `totalAssets()` is calculated by taking the balance of the contract directly (`ERC20(asset()).balanceOf(address(this));`), a user may redeem their shares before the vault has been fully funded, and take less than their share of the balance, benefiting the other withdrawer.

## Proof of Concept
* A depositor decides to withdraw from the PublicVault and receives WithdrawProxy shares in return
  * A malicious actor deposits a small amount of the underlying asset into the WithdrawProxy, making `totalAssets() > 0`
  * The depositor accidentally redeems, or is tricked into redeeming, from the WithdrawProxy, getting only a share of the small amount of the underlying asset rather than their share of the full withdrawal
  * PublicVault properly processes epoch and full withdrawReserve is sent to WithdrawProxy
  * All remaining holders of WithdrawProxy shares receive an outsized share of the withdrawReserve

## Recommendation
Add an additional storage variable that is explicitly switched to `open` when it is safe to withdraw funds.

This is intentional, the UI will block people from redeeming early. The option is there both to save some gas, and as a last resort if an LP urgently needs money (it will only make it better for the rest of the LPs).

I do consider this a valid medium severity issue, considering there is the `onlyWhenNoActiveAuction` so the intent of the code is not to block people from redeeming early but to prevent them from doing so. Note that the sponsor is right to highlight that it could be desirable to have an `emergencyRedeemFunction` where LPs do not wait for the completion of auctions.
