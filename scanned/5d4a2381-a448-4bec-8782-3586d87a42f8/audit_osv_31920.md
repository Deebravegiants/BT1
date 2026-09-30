# [C] fs/netfs/read_collect: add to next->prev_donated

## Summary
Severity: Critical
Advisory: CVE-2025-21988
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-21988
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/netfs/read_collect: add to next->prev_donated

If multiple subrequests donate data to the same "next" request
(depending on the subrequest completion order), each of them would
overwrite the `prev_donated` field, causing data corruption and a
BUG() crash ("Can't donate prior to front").

## References
- https://git.kernel.org/stable/c/62b9ad7e52d4777f7e775ee1f0ad2452f6041024
- https://git.kernel.org/stable/c/e25cec3b76aba47a49138d2162fc809c6cd49c9e
- https://git.kernel.org/stable/c/e2d46f2ec332533816417b60933954173f602121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21988.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
