# [H] CVE-2026-47895

## Summary
Severity: High
Advisory: CVE-2026-47895
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-47895
Type: osv

## Details
In strongSwan before 6.0.7, identity parsing/cloning is mishandled. Parsed EAP-Identities that result in an empty but non-NULL encoding are not correctly cloned and trigger a double-free once the duplicates are destroyed.

## References
- https://github.com/strongswan/strongswan/releases/tag/6.0.7
- https://www.strongswan.org/download.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47895.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47895
