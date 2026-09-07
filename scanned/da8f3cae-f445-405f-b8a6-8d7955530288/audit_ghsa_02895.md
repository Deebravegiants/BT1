# [C] Vulnerability in remove function leads to arbitrary code execution via filePath parameters

## Summary
Severity: Critical
Advisory: GHSA-9cq3-fj2h-ggj5
CVE: CVE-2020-36379
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-02
Source: https://github.com/advisories/GHSA-9cq3-fj2h-ggj5
Type: github-advisory

## Affected
- npm: `aaptjs` — affected >=0

## Details
Aaptjs is a node wraper for aapt. An issue was discovered in the remove function in shenzhim aaptjs 1.3.1, allows attackers to execute arbitrary code via the filePath parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36379
- https://github.com/shenzhim/aaptjs/issues/2
- https://github.com/shenzhim/aaptjs
