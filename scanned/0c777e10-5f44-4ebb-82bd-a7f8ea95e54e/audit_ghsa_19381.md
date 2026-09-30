# [H] bigint-buffer Vulnerable to Buffer Overflow via toBigIntLE() Function

## Summary
Severity: High
Advisory: GHSA-3gc7-fjrx-p6mg
CVE: CVE-2025-3194
CWE: CWE-120
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-3gc7-fjrx-p6mg
Type: github-advisory

## Affected
- npm: `bigint-buffer` — affected >=0

## Details
Versions of the package bigint-buffer from 0.0.0 to 1.1.5 are vulnerable to Buffer Overflow in the toBigIntLE() function. Attackers can exploit this to crash the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3194
- https://github.com/no2chem/bigint-buffer
- https://github.com/no2chem/bigint-buffer/blob/master/src/index.ts#L25
- https://security.snyk.io/vuln/SNYK-JS-BIGINTBUFFER-3364597
- https://www.usenix.org/system/files/sec23fall-prepub-262_staicu.pdf
