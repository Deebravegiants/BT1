# [C] Purchasing on the `BondingCurve`

## Summary
Severity: Critical
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol
Type: audit-issue

## Details
Each instantiation of [the BondingCurve contract](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol) allows users to purchase FEI in exchange for a specified [ERC20 token](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol#L25). The [purchase function](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol#L78) allows the user to specify how many `token`s to use, and calls [getAmountOut](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol#L187) to calculate the amount of FEI they should receive in return. However, as in the `ReserveStabilizer`, `getAmountOut` uses the `readOracle` function without adjusting for the number of decimals that `token` has.

In our example WBTC `BondingCurve`, a user could provide 1 WBTC to the `BondingCurve.purchase` function before scale, which is specified as `1 * 10**8`. The contract then calculates the amount of FEI to return as `31,579 * 10**8`, which given that FEI has 18 decimals is significantly less than 1 FEI. In this case the user received less than $1 of FEI in return for their $30,000 deposit.
