# [M] Price inflation by locking CVX on behalf of VotiumStrategy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/50
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L148


# Vulnerability details



## Impact
The price of vAfEth can be inflated with severe rounding errors as a result.

## Proof of Concept
In VotiumStrategy the price of vAfEth is calculated by
```solidity
function cvxInSystem() public view returns (uint256) {
    uint256 total = ILockedCvx(VLCVX_ADDRESS).lockedBalanceOf(
        address(this)
    );
    return total + trackedCvxBalance;
}
```
```solidity
function cvxPerVotium() public view returns (uint256) {
    uint256 supply = totalSupply();
    uint256 totalCvx = cvxInSystem() - cvxUnlockObligations;
    if (supply == 0 || totalCvx == 0) return 1e18;
    return (totalCvx * 1e18) / supply;
}
```
```solidity
function price(bool _validate) external view override returns (uint256) {
    return (cvxPerVotium() * ethPerCvx(_validate)) / 1e18;
}
```
Making an initial deposit so that `supply == 1` and then making `total` very large will thus inflate the price.
`total` is [the amount locked in the CVX locker for VotiumStrategy](https://etherscan.io/address/0x72a19342e8f1838460ebfccef09f6585e32db86e#code#L1222). There is nothing that prevents an attacker from calling [`ILockedCvx(VLCVX_ADDRESS).lock(votiumStrategyAddress, ...)`](https://etherscan.io/address/0x72a19342e8f1838460ebfccef09f6585e32db86e#code#L1456) to lock funds on behalf of VotiumStrategy.
This is thus equivalent to donating underlying without increasing `supply`.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/50_
