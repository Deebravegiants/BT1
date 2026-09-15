# [M] CVE-2021-2307

## Summary
Severity: Medium
Advisory: CVE-2021-2307
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2021-04-22
Source: https://osv.dev/vulnerability/CVE-2021-2307
Type: osv

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Packaging). Supported versions that are affected are 5.7.33 and prior and 8.0.23 and prior. Easily exploitable vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all MySQL Server accessible data as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.1 Base Score 6.1 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N).

## References
- https://www.kb.cert.org/vuls/id/567764
- https://security.netapp.com/advisory/ntap-20210513-0002/
- https://www.oracle.com/security-alerts/cpuapr2021.html
