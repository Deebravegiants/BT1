# [C] Context

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
The [exchangeRateStoredInternal function](https://etherscan.io/address/0xbafe01ff935c7305907c33bf824352ee5979b526#code#F1#L339) from the `CToken` contract calculates the exchange rate between an underlying token and its cToken as follows:

![](https://i0.wp.com/blog.openzeppelin.com/wp-content/uploads/2022/03/Screen-Shot-2022-03-21-at-10.47.13-AM.png?resize=532%2C104&ssl=1)

Where:

* `exchangeRate`: the exchange rate between the underlying and the cToken, e.g., TUSD/cTUSD
* `totalCash`: the total amount of underlying held by the cToken contract (calculated by calling `underlying.balanceOf(cToken)`)
* `totalBorrows`: the total amount of underlying borrowed
* `totalReserves`: the total reserves of the market, managed by the protocol that is not intended to be borrowed
* `totalSupply`: the total supply of the cToken minted to suppliers, otherwise known as liquidity providers (LPs)

The [mintFresh function](https://etherscan.io/address/0xbafe01ff935c7305907c33bf824352ee5979b526#code#F1#L497) uses this exchange rate to calculate how many cTokens should be minted to a user that supplies underlying tokens to the market.

The `CToken` contract additionally defines the [sweepToken function](https://etherscan.io/address/0xbafe01ff935c7305907c33bf824352ee5979b526#code#F2#L268), that can be called by anyone, which moves tokens accidentally sent to the CToken contract to its admin, i.e., the Timelock. This function cannot be called for the underlying token. So, for instance, if the CDAI contract holds USDT, anyone can call the `sweepToken` function on the CDAI contract, sending the USDT balance to the Timelock contract. Notably, if anyone calls this function sending the DAI address as the parameter, the call will fail since the underlying cannot be moved to the Timelock
