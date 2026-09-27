# [H] netfs: Fix read abandonment during retry

## Summary
Severity: High
Advisory: CVE-2026-31435
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31435
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix read abandonment during retry

Under certain circumstances, all the remaining subrequests from a read
request will get abandoned during retry.  The abandonment process expects
the 'subreq' variable to be set to the place to start abandonment from, but
it doesn't always have a useful value (it will be uninitialised on the
first pass through the loop and it may point to a deleted subrequest on
later passes).

Fix the first jump to "abandon:" to set subreq to the start of the first
subrequest expected to need retry (which, in this abandonment case, turned
out unexpectedly to no longer have NEED_RETRY set).

Also clear the subreq pointer after discarding superfluous retryable
subrequests to cause an oops if we do try to access it.

## References
- https://git.kernel.org/stable/c/3e5fd8f53b575ff2188f82071da19c977ca56c41
- https://git.kernel.org/stable/c/7e57523490cd2efb52b1ea97f2e0a74c0fb634cd
- https://git.kernel.org/stable/c/8f2f2bd128a8d9edbc1e785760da54ada3df69b7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31435.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31435
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
