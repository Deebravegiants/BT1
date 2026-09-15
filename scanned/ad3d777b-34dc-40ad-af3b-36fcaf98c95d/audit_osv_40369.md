# [C] gfs2: add some missing log locking

## Summary
Severity: Critical
Advisory: CVE-2026-53049
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53049
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: add some missing log locking

Function gfs2_logd() calls the log flushing functions gfs2_ail1_start(),
gfs2_ail1_wait(), and gfs2_ail1_empty() without holding sdp->sd_log_flush_lock,
but these functions require exclusion against concurrent transactions.

To fix that, add a non-locking __gfs2_log_flush() function.  Then, in
gfs2_logd(), take sdp->sd_log_flush_lock before calling the above mentioned log
flushing functions and __gfs2_log_flush().

## References
- https://git.kernel.org/stable/c/3b28eb75afe520972bacc833850c2b30aa0824cd
- https://git.kernel.org/stable/c/49d9be0722da3a4a893ba905720cba1921834ec3
- https://git.kernel.org/stable/c/98e8bf249c790d56de1abc4a5f8bd68035a00921
- https://git.kernel.org/stable/c/bf5fcd9c37c2546beaf7b401d31aefd89017dc3d
- https://git.kernel.org/stable/c/ca95342cb1b39062a03c115830286f0a426053d5
- https://git.kernel.org/stable/c/f2f225cf505ac016132ded21690f3ba0a080a4e8
- https://git.kernel.org/stable/c/fe2c8d051150b90b3ccb85f89e3b1d636cb88ec8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53049.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53049
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
