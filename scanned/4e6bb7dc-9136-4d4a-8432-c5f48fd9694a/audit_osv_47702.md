# [H] CVE-2017-1000370

## Summary
Severity: High
Advisory: CVE-2017-1000370
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000370
Type: osv

## Details
The offset2lib patch as used in the Linux Kernel contains a vulnerability that allows a PIE binary to be execve()'ed with 1GB of arguments or environmental strings then the stack occupies the address 0x80000000 and the PIE binary is mapped above 0x40000000 nullifying the protection of the offset2lib patch. This affects Linux Kernel version 4.11.5 and earlier. This is a different issue than CVE-2017-1000371. This issue appears to be limited to i386 based systems.

## References
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/99149
- https://access.redhat.com/security/cve/CVE-2017-1000370
- https://www.exploit-db.com/exploits/42273/
- https://www.exploit-db.com/exploits/42274/
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
