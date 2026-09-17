# [C] Ray Missing Authorization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6cxr-8q3m-jwrr
CVE: CVE-2023-6020
CWE: CWE-598, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-6cxr-8q3m-jwrr
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.8.1

## Details
LFI in Ray's /static/ directory allows attackers to read any file on the server without authentication. The issue is fixed in version 2.8.1+. Ray maintainers response can be found here: https://www.anyscale.com/blog/update-on-ray-cves-cve-2023-6019-cve-2023-6020-cve-2023-6021-cve-2023-48022-cve-2023-48023

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6020
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.8.1
- https://huntr.com/bounties/83dd8619-6dc3-4c98-8f1b-e620fedcd1f6
- https://www.anyscale.com/blog/update-on-ray-cves-cve-2023-6019-cve-2023-6020-cve-2023-6021-cve-2023-48022-cve-2023-48023
