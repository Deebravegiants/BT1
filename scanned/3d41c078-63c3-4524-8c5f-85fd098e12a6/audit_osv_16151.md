# [H] CVE-2019-2800

## Summary
Severity: High
Advisory: CVE-2019-2800
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-2800
Type: osv

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Replication). Supported versions that are affected are 8.0.16 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 7.1 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H).

## References
- https://support.f5.com/csp/article/K04831884?utm_source=f5support&amp%3Butm_medium=RSS
- https://access.redhat.com/errata/RHSA-2019:2484
- https://access.redhat.com/errata/RHSA-2019:2511
- https://support.f5.com/csp/article/K04831884
- http://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
