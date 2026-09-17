# [H] Suricata uses excessive resource use in malformed ssh traffic parsing

## Summary
Severity: High
Advisory: CVE-2024-28870
Aliases: GHSA-mhhx-xw7r-r5c8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-28870
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine developed by the OISF and the Suricata community. When parsing an overly long SSH banner, Suricata can use excessive CPU resources, as well as cause excessive logging volume in alert records. This issue has been patched in versions 6.0.17 and 7.0.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28870.json
- https://github.com/OISF/suricata/security/advisories/GHSA-mhhx-xw7r-r5c8
- https://nvd.nist.gov/vuln/detail/CVE-2024-28870
