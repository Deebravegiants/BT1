# [M] Incomplete fix for GHSA-rpcw-q5mr-gq35: NU5 block body poisoning via bad-blk-sigops

## Summary
Severity: Medium
Chain: Zcash
Component: zcash/zcash
Published: 2026-07-13
Source: https://github.com/zcash/zcash/security/advisories/GHSA-qvwc-hc2r-82qv
Type: github-advisory

## Details
### Summary

The fix for GHSA-rpcw-q5mr-gq35 appears incomplete. A NU5 block body/header mismatch can still permanently poison a valid block header through the `bad-blk-sigops` rejection path.

A remote unauthenticated peer can mutate authorizing data in a NU5 v5 transaction `scriptSig` so that the block keeps the same txid Merkle root and header hash, but exceeds `MAX_BLOCK_SIGOPS`. The mutated body is rejected by `CheckBlock()` as `bad-blk-sigops` before the NU5 auth-data/block-commitment mismatch check runs. Because this rejection does not set `corruptionIn=true`, `AcceptBlock()` marks the shared block header as `BLOCK_FAILED_VALID`. The genuine block body for the same header is then rejected as `duplicate-invalid`.

This is a surviving trigger path for the same class of block-body poisoning that GHSA-rpcw-q5mr-gq35 intended to prevent.

### Details

Tested against:

```text
Zcash Daemon version v6.12.3-db3082b0b
commit db3082b0bed7005c1688b901b85e417635ef3adf
```

The problematic rejection is in `CheckBlock()`:

```cpp
// src/main.cpp
if (nSigOps > MAX_BLOCK_SIGOPS)
    return state.DoS(100, error("CheckBlock(): out-of-bounds SigOpCount"),
                     REJECT_INVALID, "bad-blk-sigops");
```

`CValidationState::DoS()` defaults `corruptionIn` to false:

```cpp
// src/consensus/validation.h
virtual bool DoS(
    int level,
    bool ret = false,
    unsigned int chRejectCodeIn = 0,
    const std::string& strRejectReasonIn = "",
    bool corruptionIn = false,
    const std::string& strDebugMessageIn = "")
```

_Trimmed to 38 lines — full report: https://github.com/zcash/zcash/security/advisories/GHSA-qvwc-hc2r-82qv_
