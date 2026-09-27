# [H] FreePBX: Unauthenticated Use of Hard-Coded Credentials Vulnerability in FreePBX UCP Interface

## Summary
Severity: High
Advisory: CVE-2026-46376
Aliases: GHSA-m55x-h47x-v3gx
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-46376
Type: osv

## Details
FreePBX is an open source IP PBX. From 15.0.42 to before 16.0.45 and 17.0.7, unauthenticated users may be able to access the User Control Panel (UCP) using hard-coded initial template credentials if these were not immediately changed by the Administrator who enabled UCP. Authenticated access to ACP is required for the initial setup of UCP generic templates, but after that, without further steps by the admin, unauthenticated users may be able to gain access. This vulnerability is fixed in 16.0.45 and 17.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46376.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-m55x-h47x-v3gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46376
