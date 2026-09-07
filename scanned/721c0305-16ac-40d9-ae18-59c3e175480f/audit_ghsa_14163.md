# [M] Stored cross site scripting in Microbin

## Summary
Severity: Medium
Advisory: GHSA-mphm-gqh9-q59x
CVE: CVE-2023-27075
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-04
Source: https://github.com/advisories/GHSA-mphm-gqh9-q59x
Type: github-advisory

## Affected
- crates.io: `microbin` — affected >=0 <1.2.1

## Details
A cross-site scripting vulnerability (XSS) in the component microbin/src/pasta.rs of Microbin v1.2.0 allows attackers to execute arbitrary web scripts or HTML via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27075
- https://github.com/szabodanika/microbin/issues/142
- https://github.com/szabodanika/microbin/pull/143
- https://github.com/szabodanika/microbin/pull/143/commits/6907bb4f13faf13e45d4a2cd0f9a8c562086e6ca
- https://github.com/szabodanika/microbin
