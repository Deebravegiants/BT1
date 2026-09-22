# [M] CVE-2017-15364

## Summary
Severity: Medium
Advisory: CVE-2017-15364
Aliases: GHSA-5gxp-c379-pj42
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-15
Source: https://osv.dev/vulnerability/CVE-2017-15364
Type: osv

## Details
The foreach function in ext/ccsv.c in Ccsv 1.1.0 allows remote attackers to cause a denial of service (double free and application crash) or possibly have unspecified other impact via a crafted file. NOTE: This has been disputed and it is argued that this is not present in version 1.1.0.

## References
- https://github.com/evan/ccsv/issues/15
- https://github.com/evan/ccsv/commit/24e0b9b94c44a15b23475e821366239d53764dbd
- https://github.com/evan/ccsv/commit/c59d960ffa6b742a0616a209442618462142e6c1#diff-e39824a4819928ff248d5e90a12d1b311db2923907171cdc0ad7058da12244d9R224
