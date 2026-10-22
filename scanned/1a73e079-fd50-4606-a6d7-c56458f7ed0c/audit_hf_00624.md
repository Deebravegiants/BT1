# [M] M-22 | Broker Can Abuse oracleSigner Signatures

## Summary
Severity: Medium
Contest weight: 0.1117
Dataset id: 2123
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MuxPriceProvider contract does not include oracleData.oracleId in the message that is signed and verified. The signed message is built as: bytes32 message = ECDSAUpgradeable.toEthSignedMessageHash(keccak256(abi.encodePacked( Block.chainid, address(this), oracleData.sequence, oracleData.price, oracleData.timestamp))); Because the oracleId is not part of the signed data, a malicious broker can exploit this by taking a valid signature intended for one asset and using it to update the price of another asset. By calling the setPrices function with a different oracleId but supplying the same oracleData and signature, they can manipulate the price feeds of other assets.

## Recommendation
The oracleId must be included in the message that is signed by the oracleSigner and verified in the getOraclePrice function. This ensures that each signature is uniquely tied to a specific asset.
