# [C] CPM token price is susceptible to manipulation

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The calculation of the CPM token price is based on the combined value of the Ether and ERC20 Token liquidity that can be withdrawn per CPM token. 

This can be represented simply as `Price = (EtherValue  + TokenAmount*EthPriceOfToken) / CpmTotalSupply`, where `EthPriceOfToken` is taken from the chainlink oracle. 

However this calculation does not properly account for the Constant Price Model which is susceptible to price slippage at larger trading volumes. This would enable an attacker to make a large trade (possibly funded by a Flash Loan), shifting the balance of the ETH and Token reserves, and reducing the real value of the liquidity held in the exchange.

One way to think of this is that for any given price, there is a "correct" ratio of ETH to Token in the reserve. 

The consequence of this issue is that the wrong price is returned, which breaks the security model of this contract.
