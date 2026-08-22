# [C] Transaction header_deps validation issue (network forking)

## Summary
Severity: Critical
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-11-02
Source: https://github.com/nervosnetwork/ckb/security/advisories/GHSA-7fw6-6mfj-g3q2
Type: github-advisory

## Details
### Impact
fn `HeaderChecker#check_valid` skipped main chain checking after this PR: https://github.com/nervosnetwork/ckb/pull/1646/files#diff-c4e017b67c1b3005ca0c446a9b0879571aa36a858b1f7ddd1b9328a884e3214bR171-R176

It will cause network forking if one transaction is using a forked block header which is not exists in local node's storage.

### Patches

0.101.1 and later versions
