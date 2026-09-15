# [H] Suricata oversized resource names utilizing DNS name compression can lead to resource starvation

## Summary
Severity: High
Advisory: CVE-2024-55628
Aliases: GHSA-96w4-jqwf-qx2j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-55628
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to version 7.0.8, DNS resource name compression can lead to small DNS messages containing very large hostnames which can be costly to decode, and lead to very large DNS log records. While there are limits in place, they were too generous. The issue has been addressed in Suricata 7.0.8.

## References
- https://redmine.openinfosecfoundation.org/issues/7280
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55628.json
- https://github.com/OISF/suricata/security/advisories/GHSA-96w4-jqwf-qx2j
- https://nvd.nist.gov/vuln/detail/CVE-2024-55628
- https://github.com/OISF/suricata/commit/19cf0f81335d9f787d587450f7105ad95a648951
- https://github.com/OISF/suricata/commit/37f4c52b22fcdde4adf9b479cb5700f89d00768d
- https://github.com/OISF/suricata/commit/3a5671739f5b25e5dd973a74ca5fd8ea40e1ae2d
