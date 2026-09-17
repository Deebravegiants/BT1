# [C] iccDEV has a Use After Free vulnerability in CIccCmm class via improper hint manager object deletion

## Summary
Severity: Critical
Advisory: CVE-2026-21675
Aliases: GHSA-wcwx-794g-g78f
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2026-21675
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Versions 2.3.1 and below contain a Use After Free vulnerability in the CIccXform::Create() function, where it deletes the hint. This issue is fixed in version 2.3.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21675.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-wcwx-794g-g78f
- https://nvd.nist.gov/vuln/detail/CVE-2026-21675
- https://github.com/InternationalColorConsortium/iccDEV/issues/182
- https://github.com/InternationalColorConsortium/iccDEV/commit/510baf58fa48e00ebbb5dd577f0db4af8876bb31
