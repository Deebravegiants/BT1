# [H] CRI-O incorrect handling of supplementary groups may lead to sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-phjr-8j92-w5v7
CVE: CVE-2022-2995
CWE: CWE-284, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-20
Source: https://github.com/advisories/GHSA-phjr-8j92-w5v7
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.25.0

## Details
Incorrect handling of the supplementary groups in the CRI-O container engine might lead to sensitive information disclosure or possible data modification if an attacker has direct access to the affected container where supplementary groups are used to set access permissions and is able to execute a binary code in that container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2995
- https://github.com/cri-o/cri-o/pull/6159
- https://github.com/cri-o/cri-o/commit/db3b399a8d7dabf7f073db73894bee98311d7909
- https://github.com/cri-o/cri-o
- https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation
