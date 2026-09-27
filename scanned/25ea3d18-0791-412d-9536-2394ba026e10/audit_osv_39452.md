# [H] Suricata nfs: unbounded stateful structures can lead to resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-45766
Aliases: GHSA-jqr4-ch38-wvm6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45766
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, certain NFS parser state structures were insufficiently bounded. Crafted NFS traffic may cause Suricata to consume excessive memory, potentially resulting in denial of service. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, disable NFS application-layer parsing if it is not needed.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8418
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45766.json
- https://github.com/OISF/suricata/security/advisories/GHSA-jqr4-ch38-wvm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45766
