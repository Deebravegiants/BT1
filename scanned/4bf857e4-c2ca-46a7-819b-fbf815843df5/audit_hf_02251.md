# [H] Possible Draining of Funds Via ExchangeRate Manipulation

## Summary
Severity: High
Contest weight: 0.6004
Dataset id: 12383
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the LayerBank protocol is in essence an over-collateralized lending pool that has the lending functionality and supports a number of normal lending functionalities. While reviewing the exchange rate calculation, we notice the current implementation resets the exchange rate to 1e18 if the totalSupply is smaller than the configured DUST threshold. This design may need to be revisited. To elaborate, we show below the related exchangeRate()/updateSupplyInfo() routines. The first routine is used to compute current exchange rate while the second routine updates the user supply information as well as the total supply. It comes to our attention that the exchange rate will be reset to 1e18, which allows a malicious actor to manipulate and steal the market funds.
```solidity
function exchangeRate() public view override returns(uint256) {
    if(totalSupply == 0) return 1e18;
    Constant.AccrueSnapshot memory snapshot = pendingAccrueSnapshot();
    return getCashPrior().add(snapshot.totalBorrow).sub(snapshot.totalReserve).mul(1e18).div(totalSupply);
}

function updateSupplyInfo(address account, uint256 addAmount, uint256 subAmount) internal {
    accountBalances[account] = accountBalances[account].add(addAmount).sub(subAmount);
    totalSupply = totalSupply.add(addAmount).sub(subAmount);
    totalSupply = (totalSupply < DUST) ? 0 : totalSupply;
}
```

## Recommendation
Revisit the above routine to properly ensure the exchange rate will be not abused to steal market funds.
