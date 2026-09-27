# [H] CVE-2017-17740

## Summary
Severity: High
Advisory: CVE-2017-17740
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-18
Source: https://osv.dev/vulnerability/CVE-2017-17740
Type: osv

## Details
contrib/slapd-modules/nops/nops.c in OpenLDAP through 2.4.45, when both the nops module and the memberof overlay are enabled, attempts to free a buffer that was allocated on the stack, which allows remote attackers to cause a denial of service (slapd crash) via a member MODDN operation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00058.html
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- http://www.openldap.org/its/index.cgi/Incoming?id=8759
- https://www.oracle.com/security-alerts/cpuapr2022.html
