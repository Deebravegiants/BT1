# [H] CVE-2019-0211

## Summary
Severity: High
Advisory: CVE-2019-0211
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-0211
Type: osv

## Details
In Apache HTTP Server 2.4 releases 2.4.17 to 2.4.38, with MPM event, worker or prefork, code executing in less-privileged child processes or threads (including scripts executed by an in-process scripting interpreter) could execute arbitrary code with the privileges of the parent process (usually root) by manipulating the scoreboard. Non-Unix systems are not affected.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-0211
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00061.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00084.html
- http://packetstormsecurity.com/files/152386/Apache-2.4.38-Root-Privilege-Escalation.html
- http://www.apache.org/dist/httpd/CHANGES_2.4.39
- http://www.openwall.com/lists/oss-security/2019/04/02/3
- http://www.securityfocus.com/bid/107666
- https://access.redhat.com/errata/RHBA-2019:0959
- https://access.redhat.com/errata/RHSA-2019:0746
- https://access.redhat.com/errata/RHSA-2019:0980
- https://access.redhat.com/errata/RHSA-2019:1296
- https://access.redhat.com/errata/RHSA-2019:1297
- https://access.redhat.com/errata/RHSA-2019:1543
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ALIR5S3O7NRHEGFMIDMUSYQIZOE4TJJN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZRMTEIGZKYFNGIDOTXN3GNEJTLVCYU7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WETXNQWNQLWHV6XNW6YTO5UGDTIWAQGT/
- https://seclists.org/bugtraq/2019/Apr/5
- https://security.gentoo.org/glsa/201904-20
