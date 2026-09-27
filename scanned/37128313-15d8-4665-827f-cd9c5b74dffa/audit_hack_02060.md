# [M] 6.1 Cached Rate May Be Wrong

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Risk Accepted

OracleMulti allows to read rates from Chainlink and Uniswap circuits with _readAll(). First the
Uniswap rate is computed. However, the Uniswap circuit may not be final, meaning that the last pair (e.g.
WETH to USD) requires a Chainlink rate. Next the Chainlink rate is read from the circuit. The rate of the
last Chainlink circuit pair is cached, to be used for further computations on the Uniswap rate.

However, the constructor allows for the last Chainlink and Uniswap pairs to be different. Thus, the
following scenario is possible:

```
1.OracleMulti is initialized with a Chainlink circuit (UNI-WBTC, WBTC-USD) and a Uniswap circuit
(UNI-WETH). That means that the Uniswap is not final and a Chainlink rate has to be read for the
rate WETH-USD.
2.The Chainlink rate is calculated and the WBTC-USD rate is cached.
3.The Uniswap UNI-WETH rate is computed. Inside the branch if (uniFinalCurrency > 0) the
calculation of the rate is finalized using the cached WBTC-USD rate which leads to an incorrect
result, as the rate for WETH-USD should have been used instead.
```

Risk accepted:

Angle will make sure that the Uniswap and Chainlink circuits are compatible. A comment has been made
in the code.
