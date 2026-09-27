# [H] Suricata dnp3: unbounded reassembly can lead to resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-45765
Aliases: GHSA-m8x4-c78g-r4vj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45765
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, DNP3 reassembly could buffer data without sufficient parser-level bounds. Crafted DNP3 traffic may cause Suricata to consume excessive memory, potentially resulting in denial of service. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, disable DNP3 (which is not enabled by default) if it is not needed, and/or define a limited `stream.reassembly.depth` (0 or absent is unlimited).

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8460
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45765.json
- https://github.com/OISF/suricata/security/advisories/GHSA-m8x4-c78g-r4vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45765
