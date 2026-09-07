# [M] Upgraded Q -> 2 from #42 [1684786437801]

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-22
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/77
Type: code-finding

## Details
Judge has assessed an item in Issue #42 as 2 risk. The relevant finding follows:

 While the "division before multiplication" issues described in M-01 have been mitigated in the proposed changeset, there are other cases which should be addressed too.

Technical Details
In SafEth::stake the calculation of preDepositPrice (now present in the function approxPrice()) multiplies underlyingValue by 1e18, but underlyingValue is first divided by 1e18:
https://github.com/asymmetryfinance/smart-contracts/blob/fixMath/contracts/SafEth/SafEth.sol#L356-L370

function approxPrice() public view returns (uint256) {
    uint256 safEthTotalSupply = totalSupply();
    uint256 underlyingValue = 0;
    uint256 count = derivativeCount;

    for (uint256 i = 0; i < count; i++) {
        if (!derivatives[i].enabled) continue;
        IDerivative derivative = derivatives[i].derivative;
        underlyingValue +=
            (derivative.ethPerDerivative() * derivative.balance()) /
            1e18;
    }
    if (safEthTotalSupply == 0 || underlyingValue == 0) return 1e18;
    return (1e18 * underlyingValue) / safEthTotalSupply;
}
Also in SafEth::stake, something similar happens with totalStakeValueEth, as this is the sum of derivativeReceivedEthValue that is divided by 1e18, but then totalStakeValueEth is multiplied by 1e18 in the calculation of mintAmount:
https://github.com/asymmetryfinance/smart-contracts/blob/fixMath/contracts/SafEth/SafEth.sol#L97-L114

uint256 totalStakeValueEth = 0; // total amount of derivatives staked by user in eth
for (uint256 i = 0; i < count; i++) {
    if (!derivatives[i].enabled) continue;
    uint256 weight = derivatives[i].weight;
    if (weight == 0) continue;
    IDerivative derivative = derivatives[i].derivative;
    uint256 ethAmount = (msg.value * weight) / totalWeight;

    if (ethAmount > 0) {
        // This is slightly less than ethAmount because slippage
        uint256 depositAmount = derivative.deposit{value: ethAmount}();
        uint256 derivativeReceivedEthValue = (derivative

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/77_
