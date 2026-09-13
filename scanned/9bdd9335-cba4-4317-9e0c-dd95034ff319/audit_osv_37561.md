# [H] Suricata tls: null dereference in tls.alpn rule keyword

## Summary
Severity: High
Advisory: CVE-2026-31931
Aliases: GHSA-gr22-4784-xvw3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31931
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. From version 8.0.0 to before version 8.0.4, use of the "tls.alpn" rule keyword can cause Suricata to crash with a NULL dereference. This issue has been patched in version 8.0.4.

## References
- https://redmine.openinfosecfoundation.org/issues/8294
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31931.json
- https://github.com/OISF/suricata/security/advisories/GHSA-gr22-4784-xvw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-31931
