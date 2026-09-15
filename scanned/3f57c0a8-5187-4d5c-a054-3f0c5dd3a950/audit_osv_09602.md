# [H] CVE-2017-1000366

## Summary
Severity: High
Advisory: CVE-2017-1000366
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000366
Type: osv

## Details
glibc contains a vulnerability that allows specially crafted LD_LIBRARY_PATH values to manipulate the heap/stack, causing them to alias, potentially resulting in arbitrary code execution. Please note that additional hardening changes have been made to glibc to prevent manipulation of stack and heap memory but these issues are not directly exploitable, as such they have not been given a CVE. This affects glibc 2.25 and earlier.

## References
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Sep/7
- https://seclists.org/bugtraq/2019/Sep/7
- http://www.debian.org/security/2017/dsa-3887
- http://www.securityfocus.com/bid/99127
- http://www.securitytracker.com/id/1038712
- https://access.redhat.com/errata/RHSA-2017:1479
- https://access.redhat.com/errata/RHSA-2017:1480
- https://access.redhat.com/errata/RHSA-2017:1481
- https://access.redhat.com/errata/RHSA-2017:1567
- https://access.redhat.com/errata/RHSA-2017:1712
- https://access.redhat.com/security/cve/CVE-2017-1000366
- https://security.gentoo.org/glsa/201706-19
- https://www.exploit-db.com/exploits/42274/
- https://www.exploit-db.com/exploits/42275/
- https://www.exploit-db.com/exploits/42276/
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- https://www.suse.com/security/cve/CVE-2017-1000366/
- https://www.suse.com/support/kb/doc/?id=7020973
- https://kc.mcafee.com/corporate/index?page=content&id=SB10205
