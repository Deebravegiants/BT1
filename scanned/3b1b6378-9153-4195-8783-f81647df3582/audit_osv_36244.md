# [H] Suricata detect/alert: heap-use-after-free on alert queue expansion

## Summary
Severity: High
Advisory: CVE-2026-22264
Aliases: GHSA-mqr8-m3m4-2hw5
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22264
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to version 8.0.3 and 7.0.14, an unsigned integer overflow can lead to a heap use-after-free condition when generating excessive amounts of alerts for a single packet. Versions 8.0.3 and 7.0.14 contain a patch. As a workaround, do not run untrusted rulesets or run with less than 65536 signatures that can match on the same packet.

## References
- https://redmine.openinfosecfoundation.org/issues/8190
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22264.json
- https://github.com/OISF/suricata/security/advisories/GHSA-mqr8-m3m4-2hw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-22264
- https://github.com/OISF/suricata/commit/549d7bf60616de8e54686a188196453b5b22f715
- https://github.com/OISF/suricata/commit/5789a3d3760dbf33d93fc56c27bd9529e5bdc8f2
- https://github.com/OISF/suricata/commit/ac1eb394181530430fb7262969f423a1bf8f209b
