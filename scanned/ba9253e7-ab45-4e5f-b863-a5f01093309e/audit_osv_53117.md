# [M] CVE-2022-2991

## Summary
Severity: Medium
Advisory: CVE-2022-2991
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2022-2991
Type: osv

## Details
A heap-based buffer overflow was found in the Linux kernel's LightNVM subsystem. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length heap-based buffer. This vulnerability allows a local attacker to escalate privileges and execute arbitrary code in the context of the kernel. The attacker must first obtain the ability to execute high-privileged code on the target system to exploit this vulnerability.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-22-960/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/drivers/lightnvm/Kconfig?h=v5.10.114&id=549209caabc89f2877ad5f62d11fca5c052e0e8
