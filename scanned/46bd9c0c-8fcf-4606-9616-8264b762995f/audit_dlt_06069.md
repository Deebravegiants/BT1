# [?] fix potential panic when checking VC++ Redistributable version

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2025-12-10
Source: https://github.com/nervosnetwork/ckb/commit/4a5fee669148e48996f0f5fce6dbed5cca48bec1
Type: security-commit

## Details
fix potential panic when checking VC++ Redistributable version

The previous code used `?` to propagate an error from
`get_vc_redist_version`, but the parent function does not return a
Result. This change uses `unwrap_or_default()` to safely handle the
absence of a version.
