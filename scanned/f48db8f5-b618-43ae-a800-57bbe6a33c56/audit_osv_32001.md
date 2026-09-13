# [H] bnxt_en: Mask the bd_cnt field in the TX BD properly

## Summary
Severity: High
Advisory: CVE-2025-22108
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22108
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.12.109, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en: Mask the bd_cnt field in the TX BD properly

The bd_cnt field in the TX BD specifies the total number of BDs for
the TX packet.  The bd_cnt field has 5 bits and the maximum number
supported is 32 with the value 0.

CONFIG_MAX_SKB_FRAGS can be modified and the total number of SKB
fragments can approach or exceed the maximum supported by the chip.
Add a macro to properly mask the bd_cnt field so that the value 32
will be properly masked and set to 0 in the bd_cnd field.

Without this patch, the out-of-range bd_cnt value will corrupt the
TX BD and may cause TX timeout.

The next patch will check for values exceeding 32.

## References
- https://git.kernel.org/stable/c/107b25db61122d8f990987895c2912927b8b6e3f
- https://git.kernel.org/stable/c/9ee185e0f15594017a6f1a191ebe6630cfea5f74
- https://git.kernel.org/stable/c/f60b41b815826f15c4d0323f923f398c423178d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22108.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
