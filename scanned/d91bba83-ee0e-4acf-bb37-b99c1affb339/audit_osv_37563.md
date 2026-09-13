# [H] Suricata stream: quadratic complexity in stream inspection

## Summary
Severity: High
Advisory: CVE-2026-31933
Aliases: GHSA-hvp5-gpr6-j4gp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31933
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to versions 7.0.15 and 8.0.4, specially crafted traffic can cause Suricata to slow down, affecting performance in IDS mode. This issue has been patched in versions 7.0.15 and 8.0.4.

## References
- https://redmine.openinfosecfoundation.org/issues/8272
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31933.json
- https://github.com/OISF/suricata/security/advisories/GHSA-hvp5-gpr6-j4gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-31933
