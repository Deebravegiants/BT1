# [H] express-cart unrestricted file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-4w62-cq5r-5mmq
CVE: CVE-2018-3758
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4w62-cq5r-5mmq
Type: github-advisory

## Affected
- npm: `express-cart` — affected >=0 <1.1.7

## Details
Unrestricted file upload (RCE) in express-cart module before 1.1.7 allows a privileged user to gain access in the hosting machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3758
- https://github.com/mrvautin/expressCart/commit/65b18cfe426fa217aa6ada1d4162891883137893
- https://hackerone.com/reports/343726
