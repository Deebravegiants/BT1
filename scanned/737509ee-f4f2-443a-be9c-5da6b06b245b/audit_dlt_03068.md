# [M] `extractTAP()` function can allow minting an infinite amount in one week, leading to a DoS attack in `emitForWeek()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1241
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L227


# Vulnerability details

## Impact
In the TapOFT contract, the emission for each week is stored in `emissionForWeek[]`. During the week, a minter can call the `extractTAP()` function to mint TAP as long as they do not exceed the limit set by `emissionForWeek[]`. However, the function `extractTAP()` does not check whether the total amount minted exceeds the limit set by `emissionForWeek[]`. Instead, it only checks that the amount being minted in this particular call does not exceed the limit.

As a result, a minter can mint an infinite amount of TAP in one week. Furthermore, when the amount of TAP minted exceeds the limit set by `emissionForWeek[]`, the value of `mintedInWeek[week]` will be larger than `emissionForWeek[week]`. This can cause a Denial of Service (DoS) attack in the next call to `emitForWeek()` due to an overflow.

```solidity
// @audit In emitForWeek()` function
uint256 unclaimed = emissionForWeek[week - 1] - mintedInWeek[week - 1];
```

## Proof of Concept
TAP is the core token of the Tapioca protocol. Even though this function can only be called by a minter, it should not allow minting an infinite amount of TAP.

If a minter makes a small mistake and mints more than `emissionForWeek[]`, the `emitForWeek()` function will be vulnerable to a DoS attack.

```solidity
function extractTAP(address _to, uint256 _amount) external notPaused {
    require(msg.sender == minter, "unauthorized");
    require(_amount > 0, "amount not valid");

    uint256 week = _timestampToWeek(block.timestamp);
    require(emissionForWeek[week] >= _amount, "exceeds allowable amount");
    _mint(_to, _amount);
    mintedInWeek[week] += _amount; // @audit not check with emissionForWeek[week], allows to mint inf amount in 1 week and make emitForWeek() DOS
    emit Minted(msg.sender, _to, _amount);
}
```
## Tools Used
Manual review

## Recommended Mitigation Steps

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1241_
