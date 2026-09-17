# [M] CVE-2020-3350

## Summary
Severity: Medium
Advisory: CVE-2020-3350
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2020-3350
Type: osv

## Details
A vulnerability in the endpoint software of Cisco AMP for Endpoints and Clam AntiVirus could allow an authenticated, local attacker to cause the running software to delete arbitrary files on the system. The vulnerability is due to a race condition that could occur when scanning malicious files. An attacker with local shell access could exploit this vulnerability by executing a script that could trigger the race condition. A successful exploit could allow the attacker to delete arbitrary files on the system that the attacker would not normally have privileges to delete, producing system instability or causing the endpoint software to stop working.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IJ67VH37NCG25PICGWFWZHSVG7PBT7MC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QM7EXJHDEZJLWM2NKH6TCDXOBP5NNYIN/
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-famp-ZEpdXy
- https://usn.ubuntu.com/4435-1/
- https://usn.ubuntu.com/4435-2/
- https://lists.debian.org/debian-lts-announce/2020/08/msg00010.html
- https://security.gentoo.org/glsa/202007-23
