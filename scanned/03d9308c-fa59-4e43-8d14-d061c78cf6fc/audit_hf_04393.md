# [M] isolateRedeem

## Summary
Severity: Medium
Contest weight: 0.6823
Dataset id: 21670
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
One of the features of this protocol is that the borrower can redeem his loan (under the **Isolate Lending**) after his loan goes into auction state (before the end of the auction) by simply invoking `IsolateLiquidation.sol#isolateRedeem()`. However, in order to keep the liquidators incentivized to launch the auction for any bad debt, the borrower could get forced to pay them some fee (called `bidFine`).

The `bidFine` is defined by two factors `bidFineFactor` and `minBidFineFactor`, both of them are updatable from `Configurator.sol#setAssetAuctionParams()`,

In case admin set them to zero, when the borrower tries to redeem his loan this logic from `IsolateLogic.sol#executeIsolateRedeem()`:

File: IsolateLogic.sol#executeIsolateRedeem()

```solidity
(, vars.bidFines[vars.nidx]) = GenericLogic.calculateNftLoanBidFine(
  debtAssetData,
  debtGroupData,
  nftAssetData,
  loanData,
  vars.priceOracle
);
```

will set the value of `vars.bidFines[vars.nidx]` to zero. After that, the flow will enter this `IF` block to transfer the `bidFine` to the liquidator who launched the auction.

File: IsolateLogic.sol#executeIsolateRedeem()

```solidity
if (loanData.firstBidder != address(0)) {
  // transfer bid fine from borrower to the first bidder
  VaultLogic.erc20TransferBetweenWallets(
    params.asset,
    params.msgSender,
    loanData.firstBidder,
    vars.bidFines[vars.nidx]
  );
}
```

In case `params.asset` is one of Revert-on-Zero-Value-Transfers tokens (in scope), the transaction will revert because it is trying to transfer zero value `vars.bidFines[vars.nidx] == 0`.

## Recommendation
File: IsolateLogic.sol#executeIsolateRedeem()

```solidity
if (loanData.firstBidder != address(0) && vars.bidFines[vars.nidx] > 0) {
  // transfer bid fine from borrower to the first bidder
  VaultLogic.erc20TransferBetweenWallets(
    params.asset,
    params.msgSender,
    loanData.firstBidder,
    vars.bidFines[vars.nidx]
  );
}
```
