# [C] CVE-2018-17825

## Summary
Severity: Critical
Advisory: CVE-2018-17825
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-01
Source: https://osv.dev/vulnerability/CVE-2018-17825
Type: osv

## Details
An issue was discovered in AdPlug 2.3.1. There are several double-free vulnerabilities in the CEmuopl class in emuopl.cpp because of a destructor's two OPLDestroy calls, each of which frees TL_TABLE, SIN_TABLE, AMS_TABLE, and VIB_TABLE.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q32A64R2APAC5PXIMSYIEFDQX5AD4GAS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U3PW6PLDTPSQQRHKTU2FB72SUB4Q66NE/
- https://github.com/adplug/adplug/issues/67
