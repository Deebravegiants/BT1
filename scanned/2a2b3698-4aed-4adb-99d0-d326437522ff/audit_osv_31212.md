# [H] CVE-2024-6174

## Summary
Severity: High
Advisory: CVE-2024-6174
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2024-6174
Type: osv

## Details
When a non-x86 platform is detected, cloud-init grants root access to a hardcoded url with a local IP address. To prevent this, cloud-init default configurations disable platform enumeration.

## References
- https://github.com/canonical/cloud-init/releases/tag/25.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6174.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6174
