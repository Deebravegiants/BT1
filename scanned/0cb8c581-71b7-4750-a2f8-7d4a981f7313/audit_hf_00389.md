# [M] Wrong skew impact spread will

## Summary
Severity: Medium
Contest weight: 0.4557
Dataset id: 1775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Wrong skew impact spread will be returned in case when there is already a short position and a trader opens a long position i.e the first long position on the same pair.  
antis-contracts/src/PairInfos.sol#L346 The function incorrectly returns 0 when openInterestUSDCLong is zero for a trading pair.  
Internal pre-conditions  
Na  
External pre-conditions  
Initially a short position must be opened on a trading pair and then the first long position should be opened.  
Attack Path  
1. Suppose there is initially some short positions opened on a trading pair i.e openInterestUSDCShort not equal to zero.  
2. Now a trader opens a long position on this trading pair which is currently short skewed. Now as the pair is short skewed currently therefore better price should be offered to the current trader i.e getSkewImpactSpread function should return negative value as the trader is trying to balance the long/short position ratio but currently 0 is returned which is incorrect.  
3. If this scenario had been reversed i.e there had been initially long position and then a short position was opened then the getskewImpactSpread function would have worked completely fine by not returning 0 instead returning a negative value.  
The long traders are not offered better prices for reducing the short skew thus there is no incentive for the traders to balance the trading pair.

## Recommendation
Modify the getSkewImpactSpread function as follows  
```solidity
function getSkewImpactSpread(uint _pairIndex, bool _isBuy, uint _leveragePosition, bool isPnl) public view returns(int256 spread){  
if(isPnl) return 0; // NO Skew Impact spread for Pnl Based orders  
int intPrecision = int(_PRECISION);  
int skewParam = pairsStorage.pairSkewImpactMultiplier(_pairIndex);  
uint openInterestUSDCLong = storageT.openInterestUSDC(_pairIndex, 0);  
uint openInterestUSDCShort = storageT.openInterestUSDC(_pairIndex, 1);  
if(openInterestUSDCLong == 0) return 0;  
if(openInterestUSDCLong + openInterestUSDCShort == 0) return 0;  
uint skewPct = _isBuy ? (1e4 * openInterestUSDCLong) / (openInterestUSDCLong + openInterestUSDCShort) : (1e4 * openInterestUSDCShort) / (openInterestUSDCLong + openInterestUSDCShort);  
uint skewPctAfter = _isBuy ? (1e4 * (openInterestUSDCLong + _leveragePosition)) / (openInterestUSDCLong + openInterestUSDCShort + _leveragePosition) : (1e4 * (openInterestUSDCShort + _leveragePosition)) / (openInterestUSDCLong + openInterestUSDCShort + _leveragePosition);  
int rawSpread = (ABDKMathQuadExt.expInt(skewPctAfter, 1e4, _PRECISION) - ABDKMathQuadExt.expInt(skewPct,1e4, _PRECISION) + ABDKMathQuadExt.expInt((1e4 - skewPctAfter), 1e4, _PRECISION) - ABDKMathQuadExt.expInt((1e4 - skewPct), 1e4, _PRECISION));  
spread = (skewParam*rawSpread)/intPrecision;  
}
```
