# [H] net/sched: mqprio: fix stack out-of-bounds write in tc entry parsing

## Summary
Severity: High
Advisory: CVE-2025-38568
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38568
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: mqprio: fix stack out-of-bounds write in tc entry parsing

TCA_MQPRIO_TC_ENTRY_INDEX is validated using
NLA_POLICY_MAX(NLA_U32, TC_QOPT_MAX_QUEUE), which allows the value
TC_QOPT_MAX_QUEUE (16). This leads to a 4-byte out-of-bounds stack
write in the fp[] array, which only has room for 16 elements (0–15).

Fix this by changing the policy to allow only up to TC_QOPT_MAX_QUEUE - 1.

## References
- https://git.kernel.org/stable/c/39491e859fd494d0b51adc5c7d54c8a7dcf1d198
- https://git.kernel.org/stable/c/66fc2ebdd9d5dd6e5a9c7edeace5a61a0ab2cd86
- https://git.kernel.org/stable/c/d00e4125680f7074c4f42ce3c297336f23128e70
- https://git.kernel.org/stable/c/f1a9dbcb7d17bf0abb325cdc984957cfabc59693
- https://git.kernel.org/stable/c/ffd2dc4c6c49ff4f1e5d34e454a6a55608104c17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38568.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
