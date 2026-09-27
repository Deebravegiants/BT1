# [M] org.apache.tika:tika-parsers has an Infinite Loop vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p699-3wgc-7h72
CVE: CVE-2018-1339
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-p699-3wgc-7h72
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-parsers` — affected >=0 <1.18

## Details
Versions of the package `org.apache.tika:tika-parsers` before version 1.18 are vulnerable to Denial of Service (DoS) via a carefully crafted (or fuzzed) file that can trigger an infinite loop via the ChmParser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1339
- https://github.com/apache/tika/commit/1b6ca3685c196cfd89f5f95c19cc919ce10c5aff#diff-43f8cbe58aaab159ce88bd95fafc46dd
- https://access.redhat.com/errata/RHSA-2018:2669
- https://github.com/apache/tika
- https://lists.apache.org/thread.html/4d2cb5c819401bb075e2a1130e0d14f0404a136541a6f91da0225828@%3Cdev.tika.apache.org%3E
