# [C] Exchanging FEI on the `ReserveStabilizer`

## Summary
Severity: Critical
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/stabilizer/ReserveStabilizer.sol#L51
Type: audit-issue

## Details
The [ReserveStabilizer contract](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/stabilizer/ReserveStabilizer.sol#L51) allows users to burn FEI in exchange for tokens. The [exchangeFei function](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/stabilizer/ReserveStabilizer.sol#L43) calls the [getAmountOut function](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/stabilizer/ReserveStabilizer.sol#L56) to calculate how many tokens the user should receive for their FEI. However `getAmountOut` uses the `readOracle` function without adjusting for the number of decimals that `token` has.

In our example, the WBTC `ReserveStabilizer` would allow a user to deposit 1 FEI (worth \~1 USD), and receive over 300,000 WBTC, worth over $10 billion. This would allow a user to drain all `token` PCV from the contract for a fraction of a dollar.
