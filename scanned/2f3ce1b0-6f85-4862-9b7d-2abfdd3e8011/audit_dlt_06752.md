# [H] wLp tokens could be stolen 

## Summary
Severity: High
Chain: Smart contract
Component: 2023-12-initcapital
Published: 2023-12-21
Source: https://github.com/code-423n4/2023-12-initcapital-findings/issues/31
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-12-initcapital/blob/main/contracts/core/PosManager.sol#L249


# Vulnerability details

`PosManager#removeCollateralWLpTo` function allows users to remove collateral wrapped in a wLp token that was previously supplied to the protocol:
```solidity
File: PosManager.sol
249:     function removeCollateralWLpTo(uint _posId, address _wLp, uint _tokenId, uint _amt, address _receiver)
250:         external
251:         onlyCore
252:         returns (uint)
253:     {
254:         PosCollInfo storage posCollInfo = __posCollInfos[_posId];
255:         // NOTE: balanceOfLp should be 1:1 with amt
256:         uint newWLpAmt = IBaseWrapLp(_wLp).balanceOfLp(_tokenId) - _amt;
257:         if (newWLpAmt == 0) { 
258:             _require(posCollInfo.ids[_wLp].remove(_tokenId), Errors.NOT_CONTAIN);
259:             posCollInfo.collCount -= 1;
260:             if (posCollInfo.ids[_wLp].length() == 0) {
261:                 posCollInfo.wLps.remove(_wLp);
262:             }
263:             isCollateralized[_wLp][_tokenId] = false;
264:         }
265:         _harvest(_posId, _wLp, _tokenId);
266:         IBaseWrapLp(_wLp).unwrap(_tokenId, _amt, _receiver);
267:         return _amt;
268:     }
```
This function could be called only from the core contract using the `decollateralizeWLp` and `liquidateWLp` functions. However, it fails to check if the specified `tokenId` belongs to the current position, this check would take place only if removing is full - meaning no lp tokens remain wrapped in the wLp (line 257).

This would allow anyone to drain any other positions with supplied wLp tokens. The attacker only needs to create its own position, supply dust amount in wLp to it, and call `decollateralizeWLp` with the desired 'tokenId', also withdrawn amount should be less than the full wLp balance to prevent check on line 257. An attacker would receive almost all lp tokens and accrued rewards from the victim's wLp. 
A similar attack for harvesting the victim's rewards could be done through the `liquidateWLp` function.

## Impact
Attacker could drain any wLp token and harvest all accrued rewards for this token.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-12-initcapital-findings/issues/31_
