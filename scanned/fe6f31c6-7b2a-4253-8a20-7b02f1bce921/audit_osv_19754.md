# [H] CVE-2021-25215

## Summary
Severity: High
Advisory: CVE-2021-25215
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-25215
Type: osv

## Details
In BIND 9.0.0 -> 9.11.29, 9.12.0 -> 9.16.13, and versions BIND 9.9.3-S1 -> 9.11.29-S1 and 9.16.8-S1 -> 9.16.13-S1 of BIND Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.11 of the BIND 9.17 development branch, when a vulnerable version of named receives a query for a record triggering the flaw described above, the named process will terminate due to a failed assertion check. The vulnerability affects all currently maintained BIND 9 branches (9.11, 9.11-S, 9.16, 9.16-S, 9.17) as well as all other versions of BIND 9.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VEC2XG4Q2ODTN2C4CGXEIXU3EUTBMK7L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZDSRPCJQ7MZC6CENH5PO3VQOFI7VSWBE/
- http://www.openwall.com/lists/oss-security/2021/04/29/1
- http://www.openwall.com/lists/oss-security/2021/04/29/2
- http://www.openwall.com/lists/oss-security/2021/04/29/3
- http://www.openwall.com/lists/oss-security/2021/04/29/4
- https://kb.isc.org/v1/docs/cve-2021-25215
- https://lists.debian.org/debian-lts-announce/2021/05/msg00001.html
- https://security.netapp.com/advisory/ntap-20210521-0006/
- https://www.debian.org/security/2021/dsa-4909
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://www.oracle.com/security-alerts/cpuoct2021.html
