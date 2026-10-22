# [H] Fees can be changed during the batch

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Shareholders can vote to change the fees. For buy orders, fees are withdrawn immediately when order is submitted and the only risk is frontrunning by the shareholder's voting contract.

For sell orders, fees are withdrawn when a trader claims an order and withdraws funds in `_claimSellOrder ` function:


**code/apps/batched-bancor-market-maker/contracts/BatchedBancorMarketMaker.sol:L790-L792**
```solidity
if (fee > 0) {
    reserve.transfer(_collateral, beneficiary, fee);
}
```

Fees can be changed between opening order and claiming this order which makes the fees unpredictable.

#### Recommendation

Fees for an order should not be updated during its lifetime.
