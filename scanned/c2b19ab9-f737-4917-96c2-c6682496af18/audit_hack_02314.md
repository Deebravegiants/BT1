# [C] Other examples

## Summary
Severity: Critical
Source: https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol#L143
Type: audit-issue

## Details
The implications of this issue are far reaching throughout the entire protocol, and so we will not explain every vulnerability caused. At a high level, other vulnerabilities include:

* The [allocate function of the BondingCurve](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/bondingcurve/BondingCurve.sol#L143), which allows PCV to be removed from the `BondingCurve` and into the rest of the protocol uses `readOracle` to calculate whether the value of the PCV held is large enough to allow the call to be successful. However the call will always fail until the amount of PCV held is `10 ** |feiDecimals - tokenDecimals|` larger than it should need to be. In the case of WBTC this would mean collecting billions of dollars to be able to remove the PCV from the contract – effectively locking it up until that happens.
* The [reweight function of the UniswapPCVController](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/UniswapPCVController.sol#L57), which rewards users for moving the FEI price back to the peg, incorrectly calculates whether a reweight should be allowed. The “distance to the peg” will be out by factors of 10, meaning that reweights will virtually always be possible.
* Additionally, when performing the reweight, the [\_rebase](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/UniswapPCVController.sol#L164) and [\_reverseReweight](https://github.com/fei-protocol/fei-protocol-core-internal/blob/f54d7bb07c55adb78e2e142e7044f60090bb7602/contracts/pcv/UniswapPCVController.sol#L181) functions will be reweighting towards an incorrect peg price for FEI.

Consider updating the `readOracle` function to return the price in terms of token units, and not whole tokens. Alternatively, consider always adjusting the price returned from `readOracle` to account for the difference in token decimal amounts of the tokens in question. Additionally, consider updating your test suite to ensure that you are testing using a diverse set of tokens reflective of a mainnet environment.

_**Update:** Fixed in [PR#69](https://github.com/fei-protocol/fei-protocol-core-internal/pull/69)._
