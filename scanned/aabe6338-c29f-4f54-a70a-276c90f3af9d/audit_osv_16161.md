# [M] CVE-2019-2819

## Summary
Severity: Medium
Advisory: CVE-2019-2819
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-2819
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Security: Audit). Supported versions that are affected are 5.6.44 and prior, 5.7.26 and prior and 8.0.16 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://support.f5.com/csp/article/K02585438?utm_source=f5support&amp%3Butm_medium=RSS
- https://access.redhat.com/errata/RHSA-2019:2484
- https://access.redhat.com/errata/RHSA-2019:2511
- https://support.f5.com/csp/article/K02585438
- https://usn.ubuntu.com/4070-1/
- http://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
