# [C] 5.1.1 Important Balancer fields can be overwritten byEndTime.

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** ManagedPool.sol#L75-L77, ManagedPool.sol#L84-L86, LegacyBasePool.sol, WordCodec.sol
**Description:** Balancer’sManagedPooluses 32 bit values forstartTimeandendTimebut it does not verify if those
values exist within that range. Values are stored in a 32-byte_miscDataslot inBasePoolvia theinsertUint32()
function. Nevertheless, this function does not strip any excess bits, resulting in other fields stored in_miscDatato
be overwritten.
In the version that Aera Vault uses only the "restrict LP" field can be overwritten and by carefully crafting the value
ofendTime, the "restrict LP" boolean can be switched off, allowing anyone to usejoinPool.
The Manager could cause this behavior via theupdateWeightsGradually()function while the Owner could do it
viaenableTradingWithWeights().
Note: This issue has been reported to Balancer by the Spearbit team.
contract ManagedPool is BaseWeightedPool, ReentrancyGuard {// f14de92ac443d6daf1f3a42025b1ecdb8918f22e
// [ 64 bits | 119 bits | 1 bit | 32 bits | 32 bits | 7 bits | 1 bit ]
// [ reserved | unused | restrict LP | end time | start time | total tokens | swap flag ]
// |MSB
function _startGradualWeightChange(uint256 startTime, uint256 endTime, ... ) ... {
...
_setMiscData(
_getMiscData().insertUint32(startTime, _START_TIME_OFFSET).insertUint32(endTime,
,! _END_TIME_OFFSET)
);// this convert the values to 32 bits
...
}
}

In the latest version ofManagedPoolmany more fields can be overwritten, including:

- LP flag
- Fee end/Fee start
- Swap flag
contract ManagedPool is BaseWeightedPool, AumProtocolFeeCache, ReentrancyGuard {// current version
// [ 64 bits | 1 bit | 31 bits | 1 bit | 31 bits | 64 bits | 32 bits | 32 bits ]
// [ swap fee | LP flag | fee end | swap flag | fee start | end swap | end wgt | start wgt ]
// |MSB LSB|

The following POC shows how fields can be manipulated.
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;
import "hardhat/console.sol";
contract checkbalancer {
uint256 private constant _MASK_1 = 2**(1) - 1;
uint256 private constant _MASK_31 = 2**(31) - 1;
uint256 private constant _MASK_32 = 2**(32) - 1;
uint256 private constant _MASK_64 = 2**(64) - 1;
uint256 private constant _MASK_192 = 2**(192) - 1;


```
// [ 64 bits | 1 bit | 31 bits | 1 bit | 31 bits | 64 bits | 32 bits | 32 bits ]
// [ swap fee | LP flag | fee end | swap flag | fee start | end swap | end wgt | start wgt ]
// |MSB LSB|
uint256 private constant _WEIGHT_START_TIME_OFFSET = 0;
uint256 private constant _WEIGHT_END_TIME_OFFSET = 32;
uint256 private constant _END_SWAP_FEE_PERCENTAGE_OFFSET = 64;
uint256 private constant _FEE_START_TIME_OFFSET = 128;
uint256 private constant _SWAP_ENABLED_OFFSET = 159;
uint256 private constant _FEE_END_TIME_OFFSET = 160;
uint256 private constant _MUST_ALLOWLIST_LPS_OFFSET = 191;
uint256 private constant _SWAP_FEE_PERCENTAGE_OFFSET = 192;
function insertUint32(bytes32 word,uint256 value,uint256 offset) internal pure returns (bytes32) {
bytes32 clearedWord = bytes32(uint256(word) & ~(_MASK_32 << offset));
return clearedWord | bytes32(value << offset);
}
function decodeUint31(bytes32 word, uint256 offset) internal pure returns (uint256) {
return uint256(word >> offset) & _MASK_31;
}
function decodeUint32(bytes32 word, uint256 offset) internal pure returns (uint256) {
return uint256(word >> offset) & _MASK_32;
}
function decodeUint64(bytes32 word, uint256 offset) internal pure returns (uint256) {
return uint256(word >> offset) & _MASK_64;
}
function decodeBool(bytes32 word, uint256 offset) internal pure returns (bool) {
return (uint256(word >> offset) & _MASK_1) == 1;
}
function insertBits192(bytes32 word,bytes32 value,uint256 offset) internal pure returns (bytes32) {
bytes32 clearedWord = bytes32(uint256(word) & ~(_MASK_192 << offset));
return clearedWord | bytes32((uint256(value) & _MASK_192) << offset);
}
constructor() {
bytes32 poolState;
bytes32 miscData;
uint startTime = 1 + 2*2**32;
uint endTime = 3 + 4*2**32 + 5*2**(32+64) + 2**(32+64+31) + 6*2**(32+64+31+1) +
,! 2**(32+64+31+1+31) + 7*2**(32+64+31+1+31+1);
poolState = insertUint32(poolState,startTime, _WEIGHT_START_TIME_OFFSET);
poolState = insertUint32(poolState,endTime, _WEIGHT_END_TIME_OFFSET);
miscData = insertBits192(miscData,poolState,0);
console.log("startTime", decodeUint32(miscData, _WEIGHT_START_TIME_OFFSET));// 1
console.log("endTime", decodeUint32(miscData, _WEIGHT_END_TIME_OFFSET)); // 3
console.log("endSwapFeePercentage", decodeUint64(miscData, _END_SWAP_FEE_PERCENTAGE_OFFSET));
,! // 4
console.log("Fee startTime", decodeUint31(miscData, _FEE_START_TIME_OFFSET));// 5
console.log("Swap enabled", decodeBool(miscData, _SWAP_ENABLED_OFFSET));// true
console.log("Fee endTime", decodeUint31(miscData, _FEE_END_TIME_OFFSET));// 6
console.log("AllowlistLP", decodeBool(miscData, _MUST_ALLOWLIST_LPS_OFFSET));//
,! true
console.log("Swap fee percentage", decodeUint64(poolState, _SWAP_FEE_PERCENTAGE_OFFSET));// 7
console.log("Swap fee percentage", decodeUint64(miscData, _SWAP_FEE_PERCENTAGE_OFFSET));// 0
,! due to miscData conversion
}
}
```
**Recommendation:** Make use of aManagedPool.solversion which solves this issue.
In the meantime, before any call is made topool.updateWeightsGradually()verify that :


- startTime<= type(uint32).max
- endTime <= type(uint32).max
**Gauntlet:** Recommendation implemented in PR #
**Spearbit:** Acknowledged. Recommendation has been implemented.
