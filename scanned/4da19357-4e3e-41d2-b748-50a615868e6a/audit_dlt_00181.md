# [C] btcd mishandles witness size checking

## Summary
Severity: Critical
Chain: Bitcoin
Component: github.com/btcsuite/btcd
CVE: CVE-2022-44797
Published: 2022-11-07
Source: https://github.com/advisories/GHSA-2chg-86hq-7w38
Type: github-advisory

## Details
btcd before 0.23.2, as used in Lightning Labs lnd before 0.15.2-beta and other Bitcoin-related products, mishandles witness size checking.

### Specific Go Packages Affected
github.com/btcsuite/btcd/wire
