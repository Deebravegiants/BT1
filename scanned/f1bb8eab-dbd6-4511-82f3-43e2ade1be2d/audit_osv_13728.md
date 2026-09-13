# [H] CVE-2018-25018

## Summary
Severity: High
Advisory: CVE-2018-25018
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2018-25018
Type: osv

## Details
UnRAR 5.6.1.7 through 5.7.4 and 6.0.3 has an out-of-bounds write during a memcpy in QuickOpen::ReadRaw when called from QuickOpen::ReadNext.

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/unrar/OSV-2018-204.yaml
- https://github.com/aawc/unrar/releases
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=9845
