# [M] OpenEMR has Broken Access Control in Report/Clients/Message List CSV Export

## Summary
Severity: Medium
Advisory: CVE-2026-25124
Aliases: GHSA-q7p5-rrwj-qmp2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25124
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, the OpenEMR application is vulnerable to an access control flaw that allows low-privileged users, such as receptionists, to export the entire message list containing sensitive patient and user data. The vulnerability lies in the message_list.php report export functionality, where there is no permission check before executing sensitive database queries. The only control in place is CSRF token verification, which does not prevent unauthorized data access if the token is acquired through other means. Version 8.0.0 fixes the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25124.json
- https://github.com/openemr/openemr/security/advisories/GHSA-q7p5-rrwj-qmp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25124
- https://github.com/openemr/openemr/commit/ad902d6892482fff2e3c56bfb15597df8b6c3beb
