# [H] Suricata allows stack overflow in transforms

## Summary
Severity: High
Advisory: CVE-2024-55605
Aliases: GHSA-x2hr-33vp-w289
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-55605
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to 7.0.8, a large input buffer to the to_lowercase, to_uppercase, strip_whitespace, compress_whitespace, dotprefix, header_lowercase, strip_pseudo_headers, url_decode, or xor transform can lead to a stack overflow causing Suricata to crash. The issue has been addressed in Suricata 7.0.8.

## References
- https://redmine.openinfosecfoundation.org/issues/7229
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55605.json
- https://github.com/OISF/suricata/security/advisories/GHSA-x2hr-33vp-w289
- https://nvd.nist.gov/vuln/detail/CVE-2024-55605
