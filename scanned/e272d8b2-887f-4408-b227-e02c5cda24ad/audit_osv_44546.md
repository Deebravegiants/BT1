# [M] A Server-Side Request Forgery (SSRF) vulnerability exists in the ONLYOFFICE ownCloud Integration plugin (version 9.12)

## Summary
Severity: Medium
Advisory: CVE-2026-84282
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-84282
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the ONLYOFFICE ownCloud Integration plugin version 9.12. The /apps/onlyoffice/ajax/settings/address endpoint does not sufficiently validate the user-supplied Document Server URL before initiating outbound connections. An authenticated administrator can manipulate the document server parameter to cause the ownCloud server to send arbitrary requests to attacker-controlled destinations, including localhost and internal network hosts. This allows internal network reconnaissance and TCP port scanning based on differences in server responses.

## References
- https://github.com/ONLYOFFICE/onlyoffice-owncloud/blob/master/controller/settingsapicontroller.php
- https://kb.cert.org/vuls/id/943094
- https://www.kb.cert.org/vuls/id/943094
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84282.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84282
