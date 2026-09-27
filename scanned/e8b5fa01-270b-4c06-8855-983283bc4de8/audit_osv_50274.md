# [C] CVE-2020-10188

## Summary
Severity: Critical
Advisory: CVE-2020-10188
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-06
Source: https://osv.dev/vulnerability/CVE-2020-10188
Type: osv

## Details
utility.c in telnetd in netkit telnet through 0.17 allows remote attackers to execute arbitrary code via short writes or urgent data, because of a buffer overflow involving the netclear and nextitem functions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K3VJ6V2Z3JRNJOBVHSOPMAC76PSSKG6A/
- http://www.openwall.com/lists/oss-security/2026/01/20/8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7FMTRRQTYKWZD2GMXX3GLZV46OLPCLVK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HLU6FL24BSQQEB2SJC26NLJ2MANQDA7M/
- https://appgateresearch.blogspot.com/2020/02/bravestarr-fedora-31-netkit-telnetd_28.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00038.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-telnetd-EFJrEzPx
- https://www.arista.com/en/support/advisories-notices/security-advisories/10702-security-advisory-48
- https://lists.debian.org/debian-lts-announce/2020/05/msg00012.html
- https://github.com/krb5/krb5-appl/blob/d00cd671dfe945791b33d4f1f6a5c57ae1667ef8/telnet/telnetd/utility.c#L205-L216
- https://www.oracle.com/security-alerts/cpuApr2021.html
