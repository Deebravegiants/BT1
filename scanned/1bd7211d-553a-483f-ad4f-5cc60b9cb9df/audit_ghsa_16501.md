# [M] kubevirt allows a local attacker to execute arbitrary code via a crafted command 

## Summary
Severity: Medium
Advisory: GHSA-4q63-mr2m-57hf
CVE: CVE-2024-33394
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-4q63-mr2m-57hf
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
An issue in kubevirt kubevirt v1.2.0 and before allows a local attacker to execute arbitrary code via a crafted command to get the token component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33394
- https://gist.github.com/HouqiyuA/1b75e23ece7ad98490aec1c887bdf49b
- https://github.com/kubevirt/kubevirt
