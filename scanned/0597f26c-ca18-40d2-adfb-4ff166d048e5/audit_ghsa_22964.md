# [M] Apache Archiva does not require entry of the administrator's password at the time of modifying a user account

## Summary
Severity: Medium
Advisory: GHSA-5p54-jj38-3hxj
CVE: CVE-2010-4408
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5p54-jj38-3hxj
Type: github-advisory

## Affected
- Maven: `org.apache.archiva:archiva` — affected >=1.0 <1.3.2

## Details
Apache Archiva 1.0 through 1.0.3, 1.1 through 1.1.4, 1.2 through 1.2.2, and 1.3 through 1.3.1 does not require entry of the administrator's password at the time of modifying a user account, which makes it easier for context-dependent attackers to gain privileges by leveraging a (1) unattended workstation or (2) cross-site request forgery (CSRF) vulnerability, a related issue to CVE-2010-3449.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4408
- https://github.com/apache/archiva
- https://web.archive.org/web/20201209001124/http://www.securityfocus.com/archive/1/514937/100/0/threaded
- http://archiva.apache.org/security.html
- http://mail-archives.apache.org/mod_mbox/archiva-users/201011.mbox/ajax/%3CAANLkTimXejHAuXdoUKLN=GkNty1_XnRCbv0YA0T2cS_2%40mail.gmail.com%3E
- http://mail-archives.apache.org/mod_mbox/archiva-users/201011.mbox/ajax/%3CAANLkTimXejHAuXdoUKLN=GkNty1_XnRCbv0YA0T2cS_2@mail.gmail.com%3E
