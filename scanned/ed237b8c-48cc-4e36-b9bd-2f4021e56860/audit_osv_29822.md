# [H] um: line: always fill *error_out in setup_one_line()

## Summary
Severity: High
Advisory: CVE-2024-46844
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46844
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.110, >=6.2.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

um: line: always fill *error_out in setup_one_line()

The pointer isn't initialized by callers, but I have
encountered cases where it's still printed; initialize
it in all possible cases in setup_one_line().

## References
- https://git.kernel.org/stable/c/289979d64573f43df1d0e6bc6435de63a0d69cdf
- https://git.kernel.org/stable/c/3bedb7ce080690d0d6172db790790c1219bcbdd5
- https://git.kernel.org/stable/c/43f782c27907f306c664b6614fd6f264ac32cce6
- https://git.kernel.org/stable/c/824ac4a5edd3f7494ab1996826c4f47f8ef0f63d
- https://git.kernel.org/stable/c/96301fdc2d533a196197c055af875fe33d47ef84
- https://git.kernel.org/stable/c/c8944d449fda9f58c03bd99649b2df09948fc874
- https://git.kernel.org/stable/c/ec5b47a370177d79ae7773858042c107e21f8ecc
- https://git.kernel.org/stable/c/fc843d3837ebcb1c16d3768ef3eb55e25d5331f2
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46844.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46844
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
