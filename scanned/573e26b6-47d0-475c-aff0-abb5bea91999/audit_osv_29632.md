# [H] md/raid1: Fix data corruption for degraded array with slow disk

## Summary
Severity: High
Advisory: CVE-2024-45023
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45023
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid1: Fix data corruption for degraded array with slow disk

read_balance() will avoid reading from slow disks as much as possible,
however, if valid data only lands in slow disks, and a new normal disk
is still in recovery, unrecovered data can be read:

raid1_read_request
 read_balance
  raid1_should_read_first
  -> return false
  choose_best_rdev
  -> normal disk is not recovered, return -1
  choose_bb_rdev
  -> missing the checking of recovery, return the normal disk
 -> read unrecovered data

Root cause is that the checking of recovery is missing in
choose_bb_rdev(). Hence add such checking to fix the problem.

Also fix similar problem in choose_slow_rdev().

## References
- https://git.kernel.org/stable/c/2febf5fdbf5d9a52ddc3e986971c8609b1582d67
- https://git.kernel.org/stable/c/c916ca35308d3187c9928664f9be249b22a3a701
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45023.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45023
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
