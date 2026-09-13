# [H] CVE-2016-3157

## Summary
Severity: High
Advisory: CVE-2016-3157
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2016-3157
Type: osv

## Details
The __switch_to function in arch/x86/kernel/process_64.c in the Linux kernel does not properly context-switch IOPL on 64-bit PV Xen guests, which allows local guest OS users to gain privileges, cause a denial of service (guest OS crash), or obtain sensitive information by leveraging I/O port access.

## References
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/84594
- http://www.securitytracker.com/id/1035308
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2971-2
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-3
- http://www.ubuntu.com/usn/USN-2996-1
- http://xenbits.xen.org/xsa/advisory-171.html
