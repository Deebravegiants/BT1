# [H] CVE-2017-1000371

## Summary
Severity: High
Advisory: CVE-2017-1000371
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000371
Type: osv

## Details
The offset2lib patch as used by the Linux Kernel contains a vulnerability, if RLIMIT_STACK is set to RLIM_INFINITY and 1 Gigabyte of memory is allocated (the maximum under the 1/4 restriction) then the stack will be grown down to 0x80000000, and as the PIE binary is mapped above 0x80000000 the minimum distance between the end of the PIE binary's read-write segment and the start of the stack becomes small enough that the stack guard page can be jumped over by an attacker. This affects Linux Kernel version 4.11.5. This is a different issue than CVE-2017-1000370 and CVE-2017-1000365. This issue appears to be limited to i386 based systems.

## References
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/99131
- https://access.redhat.com/security/cve/CVE-2017-1000371
- https://www.exploit-db.com/exploits/42273/
- https://www.exploit-db.com/exploits/42276/
