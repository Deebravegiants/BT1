# [H] wLp tokens could be stolen

## Summary
Severity: High
Contest weight: 0.9180
Dataset id: 19624
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`PosManager#removeCollateralWLpTo` function allows users to remove collateral wrapped in a wLp token that was previously supplied to the protocol:
```solidity
function removeCollateralWLpTo(uint _posId, address _wLp, uint _tokenId, uint _amt, address _receiver)
    external
    onlyCore
    returns (uint)
{
    PosCollInfo storage posCollInfo = __posCollInfos[_posId];
    // NOTE: balanceOfLp should be 1:1 with amt
    uint newWLpAmt = IBaseWrapLp(_wLp).balanceOfLp(_tokenId) - _amt;
    if (newWLpAmt == 0) { 
        _require(posCollInfo.ids[_wLp].remove(_tokenId), Errors.NOT_CONTAIN);
        posCollInfo.collCount -= 1;
        if (posCollInfo.ids[_wLp].length() == 0) {
            posCollInfo.wLps.remove(_wLp);
        }
        isCollateralized[_wLp][_tokenId] = false;
    }
    _harvest(_posId, _wLp, _tokenId);
    IBaseWrapLp(_wLp).unwrap(_tokenId, _amt, _receiver);
    return _amt;
}
```
This function could be called only from the core contract using the `decollateralizeWLp` and `liquidateWLp` functions. However, it fails to check if the specified `tokenId` belongs to the current position, this check would take place only if removing is full - meaning no lp tokens remain wrapped in the wLp (line 257).

This would allow anyone to drain any other positions with supplied wLp tokens. The attacker only needs to create its own position, supply dust amount in wLp to it, and call `decollateralizeWLp` with the desired ‘tokenId’, also withdrawn amount should be less than the full wLp balance to prevent check on line 257. An attacker would receive almost all lp tokens and accrued rewards from the victim’s wLp.

A similar attack for harvesting the victim’s rewards could be done through the `liquidateWLp` function.

## Proof of Concept
The next test added to the `tests/wrapper/TestWLp.sol` file could show an exploit scenario:
```solidity
function testExploitStealWlp() public {
    uint victimAmt = 100000000;
    // Bob open position with 'tokenId' 1
    uint bobPosId = _openPositionWithLp(BOB, victimAmt);
    // Alice open position with 'tokenId' 2 and dust amount 
    uint alicePosId = _openPositionWithLp(ALICE, 1);
    // Alice successfully de-collateralizes her own position using Bob's 'tokenId' and amounts less than Bob's position by 1 to prevent a revert
    vm.startPrank(ALICE, ALICE);
    initCore.decollateralizeWLp(alicePosId, address(mockWLpUniV2), 1, victimAmt - 1, ALICE);
    vm.stopPrank();

    emit log_uint(positionManager.getCollWLpAmt(bobPosId, address(mockWLpUniV2), 1));
    emit log_uint(IERC20(lp).balanceOf(ALICE));
}
```

## Recommendation
Consider adding a check that position holds the specified token into the `removeCollateralWLpTo` function:
```solidity
_require(__posCollInfos[_posId].ids[_wlp].contains(_tokenId), Errors.NOT_CONTAIN);
```
