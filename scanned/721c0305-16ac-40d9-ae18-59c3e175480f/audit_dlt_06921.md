# [M] Incorrect decoding in `decodeLockTwpTapDstMsg`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-tapioca
Published: 2024-03-15
Source: https://github.com/code-423n4/2024-02-tapioca-findings/issues/69
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token/blob/050e666142e61018dbfcba64d295f9c458c69700/contracts/tokens/TapTokenCodec.sol#L62


# Vulnerability details

## Impact

The decoding applied in `decodeLockTwpTapDstMsg` is incorrect as there are more than one combination of bytes that would result in the same result.

This is due to:
`uint96 duration = BytesLib.toUint96(BytesLib.slice(_msg, userOffset_, durationOffset_), 0);`
Which uses length  == durationOffset_ which is 32 instead of 12

`uint256 amount = BytesLib.toUint256(BytesLib.slice(_msg, durationOffset_, _msg.length - durationOffset_), 0);`
which uses the length of the message, instead of 32 which would be the maximum size of a u256

### POC

This was found with Medusa, using Recon

The full repo is here:
https://github.com/GalloDaSballo/omnichain-lib-fuzz (invite only)



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

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-tapioca-findings/issues/69_
