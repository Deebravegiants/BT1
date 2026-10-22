# [H] H-01 Unmitigated

## Summary
Severity: High
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/12
Type: code-finding

## Details
# Lines of code




# Vulnerability details

Mitigation of H-01: Issue NOT mitigated

## Mitigated issue
[H-01: Intrinsic arbitrage from price discrepancy](https://github.com/code-423n4/2023-09-asymmetry-findings/issues/62)

The issue was that a price discrepancy between the exchange and oracle could be exploited within AfEth for an arbitrage.

## Mitigation review
The maximum profit when the balances have converged is when the ratio is 0.5. Then the maximum profit is about 0.01 % (1.01^2/1.02). This is admittedly small, but should only be tolerable if it is completely unexploitable due to exchange and gas fees. The point of this issue is that it can be self-arbitraged ad infinitum. A bot making 0.01 % over thousands of transactions is still very profitable.

Note that even in the case the balances have converged, the profit is made on a reconvergence. When the oracle price is off the deposits are not deposited according to the ratio, which means that when the deposit is withdrawn the balances are effectively converging slightly. It is the difference between deposit and withdrawal ratio that yields the profit.

It must be noted that due to the price discrepancy the balances will always wobble. Therefore an arbitrage bot could potentially exploit the natural imbalances occurring from user activity in combination with a price discrepancy.

### The balance ratio may be deliberately skewed
In order to fully exploit the up to 2 % price discrepancy, the balances must be maximally reconverging. The intention is to keep a 50:50 ratio. The attacker can cause the balances to skew and thus an increased profit can be made from an up to 0:100 ratio converging to a 50:50 ratio.
The way he can do this is by manipulating the exchange price himself. The oracle does not detect a sudden price change so the price discrepancy can be made arbitrarily high. The attacker effectively sandwich attacks his own deposits into AfEth so that it is unevenly deposited into the strategies.
For example, suppose all prices are 1 and the balances are both 1. Manipulate the exchange price of CVX so that 1 ETH gives 0.5 votium. This means that his sandwich makes a profit of 0.5 ETH (from himself). Deposit 2 ETH into AfEth, 1 ETH goes to SafEth and 1 ETH gives 0.5 votium. The deposit is valued as 1.5 ETH and he now owns 1.5/3.5 of the AfEth shares, which are worth 3.5 ETH in total. Withdrawing these returns 1.5 ETH. The balances are now skewed to 1.14:0.86. The attacker spent 2 ETH on the deposit and withdrew 1.5 ETH, but gained 0.5 from the self-sandwich, so he has skewed the ratio for free.
Note how funds have been shifted from one asset to another. This is precisely as if AfEth has sold 0.14 vAfEth for 0.14 safEth. This is unproblematic if the price actually is 1, but if there is a discrepancy this allows for arbitrage.

This is essentially a new issue, but since it is based on the same arbitrage idea and needs the same fix, I report it only here as another way to exploit the same bug.

## Conclusion
The severity of the issue as it was originally formulated is perhaps underestimated, but in light of the new findings that the balance ratio can be deliberately skewed and that this also in itself is an even more powerful arbitrage exploit shows that this issue needs fixing.
