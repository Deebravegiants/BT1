# [M] staging: wfx: fix an error handling in wfx_init_common()

## Summary
Severity: Medium
Advisory: CVE-2022-49105
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49105
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: wfx: fix an error handling in wfx_init_common()

One error handler of wfx_init_common() return without calling
ieee80211_free_hw(hw), which may result in memory leak. And I add
one err label to unify the error handler, which is useful for the
subsequent changes.

## References
- https://git.kernel.org/stable/c/60f1d3c92dc1ef1026e5b917a329a7fa947da036
- https://git.kernel.org/stable/c/86efcb524ae1889ae73f2a2f0bb7fff2ec757ab0
- https://git.kernel.org/stable/c/93498c6e775ae91732a8109dba1bdcd324908f84
- https://git.kernel.org/stable/c/9727912e906762a63c1a667c84731d3427653f88
- https://git.kernel.org/stable/c/ab0fed1fa744173433cfd1dbaf9239f200ded650
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49105.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
