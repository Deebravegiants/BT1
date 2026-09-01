# [M] Full node denial of service via non-ASCII LongPollId in getblocktemplate

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-52731
Published: 2026-05-29
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qv2r-v3mx-f4pf
Type: github-advisory

## Details
### Am I affected

You are affected if:

1. You run `zebrad` up to and including `v4.4.1`.
2. Your `zebrad.toml` sets `rpc.listen_addr` to a TCP address (RPC server is enabled).
3. An attacker can authenticate to the RPC endpoint. With the default `enable_cookie_auth = true`, this requires the attacker to read the `.cookie` file. With `enable_cookie_auth = false`, any network client reaching the RPC port can trigger it.

### Summary

The `getblocktemplate` RPC handler panics when parsing a `LongPollId` parameter that contains non-ASCII (multi-byte UTF-8) characters. The handler performs byte-index string slicing on the user-supplied string, which panics in Rust when a byte index falls within a multi-byte character boundary. Because Zebra's release profile sets `panic = "abort"`, the panic terminates the entire node process.

### Details

The `getblocktemplate` handler receives a user-supplied `LongPollId` string and slices it at fixed byte offsets to extract the encoded tip hash and tip height. When the string contains multi-byte UTF-8 characters, a byte-index slice can land in the middle of a character, causing Rust's `str` indexing to panic with "byte index is not a char boundary."

Under the `panic = "abort"` release profile, this panic terminates the entire `zebrad` process rather than just the RPC task.

### Patches

TBD.

Replace byte-index string slicing with character-aware parsing or validate that the `LongPollId` string contains only ASCII characters before slicing.

### Workarounds

- Disable the RPC server by removing `rpc.listen_addr` from `zebrad.toml`.
- Ensure `enable_cookie_auth = true` (the default) and restrict filesystem access to the `.cookie` file.
- Place a reverse proxy in front of the RPC port that validates `LongPollId` parameters are ASCII-only before forwarding.

### Impact

A single authenticated RPC request terminates the `zebrad` process. Same impact profile as GHSA-c8w6-x74f-vmg3: repeatable on restart, affects mining pools and infrastructure that forward `getblocktemplate` calls.

### Credit

Reported by `@sangsoo-osec` via a private GitHub Security Advisory submission.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-qv2r-v3mx-f4pf_
