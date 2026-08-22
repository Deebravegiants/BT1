# [M] Chainlink price feed responses are not validated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/60
Type: code-finding

## Details
# NEW ISSUE - MITIGATION IS NOT CONFIRMED
# NEW ISSUE - MITIGATION IS NOT CONFIRMED

# [adriro-NEW-H-02] Chainlink price feed responses are not validated

Link to changesets:

- https://github.com/asymmetryfinance/smart-contracts/pull/209/files
- https://github.com/asymmetryfinance/smart-contracts/pull/242/files

## Impact

The protocol team introduced Chainlink price feeds for the Reth and WstEth derivatives in order to mitigate price manipulation attacks. 

These changes introduce new issues, as the Chainlink responses are not validated at all. This is the implementation for Reth:

https://github.com/asymmetryfinance/smart-contracts/pull/209/files#diff-6abc8f2e4ad1647a12784e9fbf18e9c5f86c05668e3e89e2a51ab569992b214fR146-L216

```solidity
function ethPerDerivative() public view returns (uint256) {
    (, int256 chainLinkRethEthPrice, , , ) = chainLinkRethEthFeed
        .latestRoundData();
    return uint256(chainLinkRethEthPrice);
}
```

In the case of the WstEth derivative, additionally, the implementation even sets the price to zero if it is negative:

https://github.com/asymmetryfinance/smart-contracts/pull/242/files#diff-ac281bf63004ef9a825c084018c54f10b03233cd4f286398f5d5e993612308b5R90-R98

```solidity
function ethPerDerivative(uint256 _amount) public view returns (uint256) {
    uint256 stPerWst = IWStETH(WST_ETH).getStETHByWstETH(10 ** 18);
    (, int256 chainLinkStEthEthPrice, , , ) = chainLinkStEthEthFeed
        .latestRoundData();
    if (chainLinkStEthEthPrice < 0) chainLinkStEthEthPrice = 0;
    uint256 ethPerWstEth = (stPerWst * uint256(chainLinkStEthEthPrice)) /
        10 ** 18;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/60_
