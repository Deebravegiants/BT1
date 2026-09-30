# [H] Suricata: Keyword tls.subjectaltname can lead to NULL-ptr deref

## Summary
Severity: High
Advisory: CVE-2025-59150
Aliases: GHSA-mhv7-qfmj-m3f3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-59150
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Version 8.0.0's usage of the tls.subjectaltname keyword can lead to a segmentation fault when the decoded subjectaltname contains a NULL byte. This issue is fixed in version 8.0.1. To workaround this issue, disable rules using the tls.subjectaltname keyword.

## References
- https://forum.suricata.io/t/suricata-8-0-1-and-7-0-12-released/6018
- https://redmine.openinfosecfoundation.org/issues/7881
- https://www.vicarius.io/vsociety/posts/cve-2025-59150-suricata-detection-script
- https://www.vicarius.io/vsociety/posts/cve-2025-59150-suricata-mitigation-script
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59150.json
- https://github.com/OISF/suricata/security/advisories/GHSA-mhv7-qfmj-m3f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59150
- https://github.com/OISF/suricata/commit/d590fdfe42e995fd558315f0c24f9a352e21479d
