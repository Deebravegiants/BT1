# [M] Incorrect decoding in `decodeLockTwpTapDstMsg`

## Summary
Severity: Medium
Contest weight: 0.5886
Dataset id: 20789
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The decoding applied in `decodeLockTwpTapDstMsg` is incorrect as there are more than one combination of bytes that would result in the same result.

This is due to: `uint96 duration = BytesLib.toUint96(BytesLib.slice(_msg, userOffset_, durationOffset_), 0);` , which uses length `== durationOffset_` which is 32 instead of 12.

`uint256 amount = BytesLib.toUint256(BytesLib.slice(_msg, durationOffset_, _msg.length - durationOffset_), 0);` uses the length of the message, instead of 32 which would be the maximum size of a u256.

## Proof of Concept
This was found with Medusa, using Recon.

The test is as follows:
```solidity
function malformedTokenTwTapPositionMsg(bytes memory encoded) public {
    LockTwTapPositionMsg memory decoded = TapTokenCodec.decodeLockTwpTapDstMsg(encoded);
    bytes memory ReEncoded = TapTokenCodec.buildLockTwTapPositionMsg(decoded);

    emit DebugBytes(encoded);
    emit DebugBytes(ReEncoded);
    t(BytesLib.equal(encoded, ReEncoded), "tokenTwTapPositionMsg");
}
```
And a repro case is:
```solidity
function test_malformedTokenTwTapPositionMsg_codec() public {
    malformedTokenTwTapPositionMsg(624640ab9f2104f27610f40e02a5184fc6e28e66473292539dccd55a499f6ce9e6103ab8afd0ef7ebd66e9b36707fb0a70bd2db5189ae20d11df6743e19fd653638b193c3e611e038a16fcc61179eebc1d4c);
}
```

## Recommendation
Change:
`uint96 duration = BytesLib.toUint96(BytesLib.slice(_msg, userOffset_, durationOffset_), 0);`
to
`uint96 duration = BytesLib.toUint96(BytesLib.slice(_msg, userOffset_, 12), 0);`, which will prevent reading the wrong area of memory.

Change:
`uint256 amount = BytesLib.toUint256(BytesLib.slice(_msg, durationOffset_, _msg.length - durationOffset_), 0);`
to
`uint256 amount = BytesLib.toUint256(BytesLib.slice(_msg, durationOffset_, 32), 0);`, which will ensure that the bytes being read are the length of the message, instead of 32 which would be the maximum size of a u256.
