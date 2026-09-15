# [H] Suricata 's http2 parser contains an improper compressed header handling can lead to resource starvation

## Summary
Severity: High
Advisory: CVE-2024-32663
Aliases: GHSA-9jxm-qw9v-266r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/CVE-2024-32663
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to 7.0.5 and 6.0.19, a small amount of HTTP/2 traffic can lead to Suricata using a large amount of memory. The issue has been addressed in Suricata 7.0.5 and 6.0.19. Workarounds include disabling the HTTP/2 parser and reducing `app-layer.protocols.http2.max-table-size` value (default is 65536).

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00029.html
- https://redmine.openinfosecfoundation.org/issues/6892
- https://redmine.openinfosecfoundation.org/issues/6900
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32663.json
- https://github.com/OISF/suricata/security/advisories/GHSA-9jxm-qw9v-266r
- https://nvd.nist.gov/vuln/detail/CVE-2024-32663
- https://github.com/OISF/suricata/commit/08d93f7c3762781b743f88f9fdc4389eb9c3eb64
- https://github.com/OISF/suricata/commit/c0af92295e833d1db29b184d63cd3b829451d7fd
- https://github.com/OISF/suricata/commit/d24b37a103c04bb2667e449e080ba4c8e56bb019
- https://github.com/OISF/suricata/commit/e68ec4b227d19498f364a41eb25d3182f0383ca5
