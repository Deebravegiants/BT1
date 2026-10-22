# [M] removeLiquidityBySigV2 does not correctly hash its contents to comply with EIP-712

## Summary
Severity: Medium
Contest weight: 0.5713
Dataset id: 14747
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
removeLiquidityBySigV2 hashes the signature as shown below but doesn't fully hash it to comply with EIP-712.
```solidity
Signature.validateRecoveredAddress(
    Signature.calculateDigest(
        keccak256(
            abi.encode(
                REMOVE_LIQUIDITY_V2_TYPEHASH,
                block.chainid,
                msg.sender,
                owner,
                poolId,
                abi.encode(
                    REMOVE_LIQUIDITY_V2_INPUT_TYPEHASH,
                    input.token,
                    input.sharesAmount,
                    input.receiver,
                    input.minOut
                ),
                Signature.incrementSigNonce(owner),
                sig.deadline,
                keccak256(extraSignatureData)
            )
        ),
    owner,
)
```
The RemoveLiquidityV2Input struct is only encoded, not hashed as required by the standard.
The struct values are encoded recursively as hashStruct(value).
As a result, EIP-compliant signers will have issues when attempting to use the removeLiquidityBySigV2 function.

## Recommendation
Hash the contents of the RemoveLiquidityV2Input struct.
```solidity
Signature.validateRecoveredAddress(
    Signature.calculateDigest(
        keccak256(
            abi.encode(
                REMOVE_LIQUIDITY_V2_TYPEHASH,
                block.chainid,
                msg.sender,
                owner,
                poolId,
                keccak256(
                    abi.encode(
                        REMOVE_LIQUIDITY_V2_INPUT_TYPEHASH,
                        input.token,
                        input.sharesAmount,
                        input.receiver,
                        input.minOut
                    )
                ),
                Signature.incrementSigNonce(owner),
                sig.deadline,
                keccak256(extraSignatureData)
            )
        ),
    owner,
)
```
