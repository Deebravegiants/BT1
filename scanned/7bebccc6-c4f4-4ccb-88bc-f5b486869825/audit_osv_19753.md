# [M] CVE-2021-25214

## Summary
Severity: Medium
Advisory: CVE-2021-25214
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-29
Source: https://osv.dev/vulnerability/CVE-2021-25214
Type: osv

## Details
In BIND 9.8.5 -> 9.8.8, 9.9.3 -> 9.11.29, 9.12.0 -> 9.16.13, and versions BIND 9.9.3-S1 -> 9.11.29-S1 and 9.16.8-S1 -> 9.16.13-S1 of BIND 9 Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.11 of the BIND 9.17 development branch, when a vulnerable version of named receives a malformed IXFR triggering the flaw described above, the named process will terminate due to a failed assertion the next time the transferred secondary zone is refreshed.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VEC2XG4Q2ODTN2C4CGXEIXU3EUTBMK7L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZDSRPCJQ7MZC6CENH5PO3VQOFI7VSWBE/
- http://www.openwall.com/lists/oss-security/2021/04/29/1
- http://www.openwall.com/lists/oss-security/2021/04/29/2
- http://www.openwall.com/lists/oss-security/2021/04/29/3
- http://www.openwall.com/lists/oss-security/2021/04/29/4
- https://kb.isc.org/v1/docs/cve-2021-25214
- https://lists.debian.org/debian-lts-announce/2021/05/msg00001.html
- https://security.netapp.com/advisory/ntap-20210521-0006/
- https://www.debian.org/security/2021/dsa-4909
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
