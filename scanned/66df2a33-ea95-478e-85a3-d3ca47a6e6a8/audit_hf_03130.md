# [H] Attacker can dispute() with malicious data and

## Summary
Severity: High
Contest weight: 0.7511
Dataset id: 17615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The data provided by the caller of dispute() can be malicious, which allows the attacker to dispute and claim bonds from honest proposers.  
Oct 3rd to Oct 5th.  
The check  
```solidity
bool nonceIsValid = dataRoundTimestamp == roundTimestamp && (nonce >> 64) == (keccak256(abi.encode(dataRoundId, uint64(roundTimestamp))) >> 64);
```
attempts to ensure that the data matches the nonce, but erroneously translates a failing match as an invalid nonce. This isn’t necessarily true as it might be the data that is malicious instead.  
The caller of dispute() can use malicious data to dispute honest proposals and claim the bonds.

## Recommendation
The pre-image check should be converted to a reverting conditional check. nonceIsValid can subsequently be renamed to timestampIsValid.  
```solidity
// Verify that `data` is the pre-image of the hash encoded within `nonce`
if ((nonce >> 64) != (keccak256(abi.encode(dataRoundId, uint64(roundTimestamp))) >> 64)) 
    revert OptimisticChainlinkOracle__validate_invalidData();
bool timestampIsValid = dataRoundTimestamp == roundTimestamp;
```
function by moving all time-related and data checks to shift(). The validate() method ensures that the roundId is correct (leads to a valid chainlink round) and that the proposed value is the same as the computed one.  
Do we still need the data parameter in dispute(), seems like it's no longer used, can we get rid of it?  
The data param in dispute is not used by the chainlink oracle but other implementations (like the proof oracles) will use it. We kept it because of that reason.  
In that case, maybe we can remove this line so it's more clear that data is not needed for Chainlink: https://github.com/fiatdao/delphi-v2/blob/608ff90d260a92d39140af4f7b73f78642c8886c/src/OptimisticChainlinkOracle.sol#L172  
Removed the data param from the validate() function.  
Confirmed.
