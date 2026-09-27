# [H] Suricata smtp/mine: quadratic complexity in extracting urls

## Summary
Severity: High
Advisory: CVE-2026-31934
Aliases: GHSA-hr89-h2pp-f3c8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-31934
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. From version 8.0.0 to before version 8.0.4, there is a quadratic complexity issue when searching for URLs in mime encoded messages over SMTP leading to a performance impact. This issue has been patched in version 8.0.4.

## References
- https://redmine.openinfosecfoundation.org/issues/8292
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31934.json
- https://github.com/OISF/suricata/security/advisories/GHSA-hr89-h2pp-f3c8
- https://nvd.nist.gov/vuln/detail/CVE-2026-31934
