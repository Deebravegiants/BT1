# [H] Suricata ja4: invalid alpn leads to panic

## Summary
Severity: High
Advisory: CVE-2024-47522
Aliases: GHSA-w5xv-6586-jpm7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-47522
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to version 7.0.7, invalid ALPN in TLS/QUIC traffic when JA4 matching/logging is enabled can lead to Suricata aborting with a panic. This issue has been addressed in 7.0.7. One may disable ja4 as a workaround.

## References
- https://redmine.openinfosecfoundation.org/issues/7267
- https://www.vicarius.io/vsociety/posts/cve-2024-47522-detect-suricata-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2024-47522-mitigate-suricata-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47522.json
- https://github.com/OISF/suricata/security/advisories/GHSA-w5xv-6586-jpm7
- https://nvd.nist.gov/vuln/detail/CVE-2024-47522
