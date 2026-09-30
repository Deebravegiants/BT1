# [C] Ghostfolio: Full-Read SSRF in Manual Asset Import

## Summary
Severity: Critical
Advisory: CVE-2026-28680
Aliases: GHSA-hhv6-c34h-pwgh
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28680
Type: osv

## Details
Ghostfolio is an open source wealth management software. Prior to version 2.245.0, an attacker can exploit the manual asset import feature to perform a full-read SSRF, allowing them to exfiltrate sensitive cloud metadata (IMDS) or probe internal network services. This issue has been patched in version 2.245.0.

## References
- https://github.com/ghostfolio/ghostfolio/releases/tag/2.245.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28680.json
- https://github.com/ghostfolio/ghostfolio/security/advisories/GHSA-hhv6-c34h-pwgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-28680
