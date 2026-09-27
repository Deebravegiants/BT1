# [C] HotCRP vulnerable to remote code execution through formulas

## Summary
Severity: Critical
Advisory: CVE-2026-23836
Aliases: GHSA-hpqh-j6qx-x57h
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23836
Type: osv

## Details
HotCRP is conference review software. A problem introduced in April 2024 in version 3.1 led to inadequately sanitized code generation for HotCRP formulas which allowed users to trigger the execution of arbitrary PHP code. The problem is patched in release version 3.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23836.json
- https://github.com/kohler/hotcrp/security/advisories/GHSA-hpqh-j6qx-x57h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23836
- https://github.com/kohler/hotcrp/commit/4674fcfbb76511072a1145dad620756fc1d4b4e9
- https://github.com/kohler/hotcrp/commit/bfc7e0db15df6ed6d544a639020d2ce05a5f0834
