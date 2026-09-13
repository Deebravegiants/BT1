# [H] Suricata ldap: unbounded responses per transaction can lead to resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-45768
Aliases: GHSA-cr4x-w4c4-57p7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45768
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Starting in version 8.0.0 and prior to version 8.0.5, LDAP transaction state could store an unbounded number of responses. Because LDAP can be processed over UDP, crafted traffic may cause Suricata to consume excessive memory, potentially resulting in denial of service. Version 8.0.5 contains a fix. As a workaround, disable LDAP application-layer parsing where it is not required. Alternatively, use a rule like `alert ldap any any -> any any (sid: 1; ldap.responses.count: >1024; bypass;)`.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8405
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45768.json
- https://github.com/OISF/suricata/security/advisories/GHSA-cr4x-w4c4-57p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-45768
