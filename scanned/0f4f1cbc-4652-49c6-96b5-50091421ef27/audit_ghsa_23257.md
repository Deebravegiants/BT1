# [H] ViMbAdmin CSRF Vulnerabilities

## Summary
Severity: High
Advisory: GHSA-rrmf-fpmm-jpwr
CVE: CVE-2017-6086
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rrmf-fpmm-jpwr
Type: github-advisory

## Affected
- Packagist: `opensolutions/vimbadmin` — affected >=0

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in the addAction and purgeAction functions in ViMbAdmin 3.0.15 allow remote attackers to hijack the authentication of logged administrators to
1. add an administrator user via a crafted POST request to `<vimbadmin directory>/application/controllers/DomainController.php`,
2. remove an administrator user via a crafted GET request to `<vimbadmin directory>/application/controllers/DomainController.php`,
3. change an administrator password via a crafted POST request to `<vimbadmin directory>/application/controllers/DomainController.php`,
4. add a mailbox via a crafted POST request to `<vimbadmin directory>/application/controllers/MailboxController.php`,
5. delete a mailbox via a crafted POST request to `<vimbadmin directory>/application/controllers/MailboxController.php`,
6. archive a mailbox address via a crafted GET request to `<vimbadmin directory>/application/controllers/ArchiveController.php`,
7. add an alias address via a crafted POST request to `<vimbadmin directory>/application/controllers/AliasController.php`, or
8. remove an alias address via a crafted GET request to `<vimbadmin directory>/application/controllers/AliasController.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6086
- https://github.com/opensolutions/ViMbAdmin/issues/250
- https://github.com/opensolutions/ViMbAdmin
- https://www.exploit-db.com/exploits/41967
- http://www.openwall.com/lists/oss-security/2017/05/03/7
