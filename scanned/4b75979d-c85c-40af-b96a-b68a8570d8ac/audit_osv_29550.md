# [H] wifi: mac80211: fix TTLM teardown work

## Summary
Severity: High
Advisory: CVE-2024-43848
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43848
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix TTLM teardown work

The worker calculates the wrong sdata pointer, so if it ever
runs, it'll crash. Fix that.

## References
- https://git.kernel.org/stable/c/2fe0a605d083b884490ee4de02be071b5b4291b1
- https://git.kernel.org/stable/c/9750899410c8478ef043c42029f4f6144c096eac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43848.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43848
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
