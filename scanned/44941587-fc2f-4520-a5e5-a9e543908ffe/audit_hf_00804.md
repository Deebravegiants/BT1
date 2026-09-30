# [M] M-05 | Incorrect Key Is Used In PositionManager

## Summary
Severity: Medium
Contest weight: 0.1034
Dataset id: 2540
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Module addresses are fetched from the Registry contract and these addresses are stored with key to address mappings. Address keys are constant variables in contracts and they are determined using keccak hashes.
SENTIMENT_POSITION_BEACON_KEY in the PositionManager contract is stated as “0xc77ea3242ed8f193508dbbe062eaeef25819b43b511cbe2fc5bd5de7e23b9990”. However, the correct hash result of keccak(SENTIMENT_POSITION_BEACON_KEY) is “0x6e7384c78b0e09fb848f35d00a7b14fc1ad10ae9b10117368146c0e09b6f2fa2”.
If the Registry contract owner uses the correct key while setting addresses, positionBeacon address in the PositionManager contract will be retrieved incorrectly from the Registry contract.

## Recommendation
Use the correct hash for constant keys.
