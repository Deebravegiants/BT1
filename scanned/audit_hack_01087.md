# [M] Aave incident: About 110 million USD in WETH, USDT, WBTC, WMATIC in Aave V2 on Polygon cannot be withdrawn, nor can it be borrowed and repaid. Th

## Summary
Severity: Medium
Target: Aave
Loss: -
Attack method: Compatibility issues
Published: 2023-05-20
Source: https://beincrypto.com/aave-users-unable-to-access-over-100m/
Type: slowmist-incident

## Details
About 110 million USD in WETH, USDT, WBTC, WMATIC in Aave V2 on Polygon cannot be withdrawn, nor can it be borrowed and repaid. This is because the interest rate strategy contract is only compatible with Ethereum, not Polygon. At present, Aave has submitted a patch to fix this problem, which will be deployed after voting. Funds are not at risk, but it takes at least a week for funds to be unfrozen.
