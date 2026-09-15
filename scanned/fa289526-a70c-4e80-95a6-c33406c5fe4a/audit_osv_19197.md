# [H] CVE-2020-8625

## Summary
Severity: High
Advisory: CVE-2020-8625
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2020-8625
Type: osv

## Details
BIND servers are vulnerable if they are running an affected version and are configured to use GSS-TSIG features. In a configuration which uses BIND's default settings the vulnerable code path is not exposed, but a server can be rendered vulnerable by explicitly setting valid values for the tkey-gssapi-keytab or tkey-gssapi-credentialconfiguration options. Although the default configuration is not vulnerable, GSS-TSIG is frequently used in networks where BIND is integrated with Samba, as well as in mixed-server environments that combine BIND servers with Active Directory domain controllers. The most likely outcome of a successful exploitation of the vulnerability is a crash of the named process. However, remote code execution, while unproven, is theoretically possible. Affects: BIND 9.5.0 -> 9.11.27, 9.12.0 -> 9.16.11, and versions BIND 9.11.3-S1 -> 9.11.27-S1 and 9.16.8-S1 -> 9.16.11-S1 of BIND Supported Preview Edition. Also release versions 9.17.0 -> 9.17.1 of the BIND 9.17 development branch

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EBTPWRQWRQEJNWY4NHO4WLS4KLJ3ERHZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KYXAF7G45RXDVNUTWWCI2CVTHRZ67LST/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QWCMBOSZOJIIET7BWTRYS3HLX5TSDKHX/
- https://kb.isc.org/v1/docs/cve-2020-8625
- https://lists.debian.org/debian-lts-announce/2021/02/msg00029.html
- https://security.netapp.com/advisory/ntap-20210319-0001/
- https://www.debian.org/security/2021/dsa-4857
- https://www.zerodayinitiative.com/advisories/ZDI-21-195/
- http://www.openwall.com/lists/oss-security/2021/02/19/1
- http://www.openwall.com/lists/oss-security/2021/02/20/2
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
