# [H] PM / devfreq: Fix leak in devfreq_dev_release()

## Summary
Severity: High
Advisory: CVE-2023-53518
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53518
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

PM / devfreq: Fix leak in devfreq_dev_release()

srcu_init_notifier_head() allocates resources that need to be released
with a srcu_cleanup_notifier_head() call.

Reported by kmemleak.

## References
- https://git.kernel.org/stable/c/111bafa210ae546bee7644be730c42df9c35b66e
- https://git.kernel.org/stable/c/1640e9c72173911ad0fddb05012c01eafe082c4e
- https://git.kernel.org/stable/c/29811f4b8255d4238cf326f3bb7129784766beab
- https://git.kernel.org/stable/c/3354c401c68d70567d1ef25d12f4e22a7813a3c6
- https://git.kernel.org/stable/c/5693d077595de721f9ddbf9d37f40e5409707dfe
- https://git.kernel.org/stable/c/64e6e0dc2d578c0a9e31cb4edd719f0a3ed98f6d
- https://git.kernel.org/stable/c/7462483446cb9986568ad7adae746ce5f18d2968
- https://git.kernel.org/stable/c/8918025feb2f5f7c73f2495c158f22997e25cb02
- https://git.kernel.org/stable/c/ab192e5e5d3b48415909a8408acfd007a607bcc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53518.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53518
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
