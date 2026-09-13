# [H] CVE-2019-1000012

## Summary
Severity: High
Advisory: CVE-2019-1000012
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000012
Type: osv

## Details
Hex package manager version 0.14.0 through 0.18.2 contains a Signing oracle vulnerability in Package registry verification that can result in Package modifications not detected, allowing code execution. This attack appears to be exploitable via victim fetches packages from malicious/compromised mirror. This vulnerability appears to have been fixed in 0.19.

## References
- https://github.com/hexpm/hex/pull/646
- https://github.com/hexpm/hex/pull/651
