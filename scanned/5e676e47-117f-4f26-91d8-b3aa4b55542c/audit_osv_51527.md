# [H] CVE-2021-31440

## Summary
Severity: High
Advisory: CVE-2021-31440
Aliases: A-189614572, PUB-A-189614572
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-21
Source: https://osv.dev/vulnerability/CVE-2021-31440
Type: osv

## Details
This vulnerability allows local attackers to escalate privileges on affected installations of Linux Kernel 5.11.15. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability. The specific flaw exists within the handling of eBPF programs. The issue results from the lack of proper validation of user-supplied eBPF programs prior to executing them. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the kernel. Was ZDI-CAN-13661.

## References
- https://security.netapp.com/advisory/ntap-20210706-0003/
- https://www.zerodayinitiative.com/advisories/ZDI-21-503/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=10bf4e83167cc68595b85fd73bb91e8f2c086e36
