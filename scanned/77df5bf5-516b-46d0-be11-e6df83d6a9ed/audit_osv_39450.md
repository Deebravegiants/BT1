# [C] Suricata http2: protocol-change type confusion can lead to denial of service

## Summary
Severity: Critical
Advisory: CVE-2026-45764
Aliases: GHSA-5rvq-72r5-rqhr
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45764
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, a protocol change while processing HTTP/2 traffic could lead to type confusion in Suricata. Crafted traffic may cause Suricata to crash, resulting in denial of service. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, disable HTTP/2 parsing if it is not required.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8492
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45764.json
- https://github.com/OISF/suricata/security/advisories/GHSA-5rvq-72r5-rqhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45764
