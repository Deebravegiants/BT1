# [H] Suricata's pgsql: memory exhaustion use on record parsing

## Summary
Severity: High
Advisory: CVE-2024-23835
Aliases: GHSA-8583-353f-mvwc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-23835
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine.  Prior to version 7.0.3, excessive memory use during pgsql parsing could lead to OOM-related crashes.  This vulnerability is patched in 7.0.3.  As workaround, users can disable the pgsql app layer parser.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GOCOBFUTIFHOP2PZOH4ENRFXRBHIRKK4/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZXJIT7R53ZXROO3I256RFUWTIW4ECK6P/
- https://redmine.openinfosecfoundation.org/issues/6411
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23835.json
- https://github.com/OISF/suricata/security/advisories/GHSA-8583-353f-mvwc
- https://nvd.nist.gov/vuln/detail/CVE-2024-23835
- https://github.com/OISF/suricata/commit/86de7cffa7e8f06fe9d600127e7dabe89c7e81dd
- https://github.com/OISF/suricata/commit/f52c033e566beafb4480c139eb18662a2870464f
