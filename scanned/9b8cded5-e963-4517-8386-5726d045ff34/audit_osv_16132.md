# [M] CVE-2019-2739

## Summary
Severity: Medium
Advisory: CVE-2019-2739
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-2739
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Security: Privileges). Supported versions that are affected are 5.6.44 and prior, 5.7.26 and prior and 8.0.16 and prior. Easily exploitable vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.1 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A55N3HZ3JZBXHQMGTUHY63FVTDU5ILEV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CN3JPT5ICOAWQNPFVPVLLYR4TQIX4MXP/
- https://support.f5.com/csp/article/K51272092?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00037.html
- http://packetstormsecurity.com/files/153862/Slackware-Security-Advisory-mariadb-Updates.html
- https://access.redhat.com/errata/RHSA-2019:2484
- https://access.redhat.com/errata/RHSA-2019:2511
- https://access.redhat.com/errata/RHSA-2019:3708
- https://seclists.org/bugtraq/2019/Aug/1
- https://support.f5.com/csp/article/K51272092
- https://usn.ubuntu.com/4070-1/
- https://usn.ubuntu.com/4070-2/
- https://usn.ubuntu.com/4070-3/
- http://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
