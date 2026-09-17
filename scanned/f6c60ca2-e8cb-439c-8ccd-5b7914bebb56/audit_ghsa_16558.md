# [H] karmada vulnerable to arbitrary code execution via a crafted command 

## Summary
Severity: High
Advisory: GHSA-wccg-v638-j9q2
CVE: CVE-2024-33396
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-wccg-v638-j9q2
Type: github-advisory

## Affected
- Go: `github.com/karmada-io/karmada` — affected >=0

## Details
An issue in karmada-io karmada v1.9.0 and before allows a local attacker to execute arbitrary code via a crafted command to get the token component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33396
- https://gist.github.com/HouqiyuA/2b56a893c06553013982836abb77ba50
- https://github.com/karmada-io/karmada
