# [C] Denial of service in message decoding in github.com/btcsuite/btcd

## Summary
Severity: Critical
Advisory: GO-2022-1098
Aliases: CVE-2022-44797, GHSA-2chg-86hq-7w38
Package: github.com/btcsuite/btcd
Published: 2022-11-08
Source: https://osv.dev/vulnerability/GO-2022-1098
Type: chain-advisory

## Affected
- Go: `github.com/btcsuite/btcd` — affected >=0 <0.23.2

## Details
Erroneous message decoding can cause denial of service.

Improper checking of maximum witness size during node message decoding prevented nodes in Lightning Labs lnd (before 0.15.2-beta) to sync.

## References
- https://github.com/advisories/GHSA-2chg-86hq-7w38
- https://github.com/lightningnetwork/lnd/issues/7002
- https://github.com/btcsuite/btcd/pull/1896/commits/f523d4ccaa5f34a2f761f16a05f5d6e6665b1168
- https://github.com/btcsuite/btcd/releases/tag/v0.23.2
