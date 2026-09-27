# [M] Permissions bypass in SmallRye

## Summary
Severity: Medium
Advisory: GHSA-54fx-gm74-q676
CVE: CVE-2020-1729
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-54fx-gm74-q676
Type: github-advisory

## Affected
- Maven: `io.smallrye.config:smallrye-config` — affected >=0 <1.6.2

## Details
A flaw was found in SmallRye's API through version 1.6.1. The API can allow other code running within the application server to potentially obtain the ClassLoader, bypassing any permissions checks that should have been applied. The largest threat from this vulnerability is a threat to data confidentiality. This is fixed in SmallRye 1.6.2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1729
- https://github.com/smallrye/smallrye-config/commit/fb0def6f61c09a2a80c9145e4ec6521225cd0b99
- https://bugzilla.redhat.com/show_bug.cgi?id=1802444
