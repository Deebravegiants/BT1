# [H] pf4j is vulnerable to Path Traversal or Zip Slip attack through improper handling of zip entry names 

## Summary
Severity: High
Advisory: GHSA-5458-7hh9-v7p4
CVE: CVE-2025-70952
CWE: CWE-22, CWE-23
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-5458-7hh9-v7p4
Type: github-advisory

## Affected
- Maven: `org.pf4j:pf4j` — affected >=0 <3.14.1

## Details
pf4j before 20c2f80 has a path traversal vulnerability in the extract() function of Unzip.java, where improper handling of zip entry names can allow directory traversal or Zip Slip attacks, due to a lack of proper path normalization and validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70952
- https://github.com/pf4j/pf4j/issues/618
- https://github.com/pf4j/pf4j/issues/623
- https://github.com/pf4j/pf4j/commit/20c2f80089d1ea779e22c2de5f109a0bce4e1b14
- https://gist.github.com/weaver4VD/410f23adb24ef5f5077f021f4393e705
- https://github.com/pf4j/pf4j
