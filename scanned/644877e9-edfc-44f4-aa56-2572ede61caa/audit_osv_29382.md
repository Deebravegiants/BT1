# [C] libceph: fix race between delayed_work() and ceph_monc_stop()

## Summary
Severity: Critical
Advisory: CVE-2024-42232
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42232
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix race between delayed_work() and ceph_monc_stop()

The way the delayed work is handled in ceph_monc_stop() is prone to
races with mon_fault() and possibly also finish_hunting().  Both of
these can requeue the delayed work which wouldn't be canceled by any of
the following code in case that happens after cancel_delayed_work_sync()
runs -- __close_session() doesn't mess with the delayed work in order
to avoid interfering with the hunting interval logic.  This part was
missed in commit b5d91704f53e ("libceph: behave in mon_fault() if
cur_mon < 0") and use-after-free can still ensue on monc and objects
that hang off of it, with monc->auth and monc->monmap being
particularly susceptible to quickly being reused.

To fix this:

- clear monc->cur_mon and monc->hunting as part of closing the session
  in ceph_monc_stop()
- bail from delayed_work() if monc->cur_mon is cleared, similar to how
  it's done in mon_fault() and finish_hunting() (based on monc->hunting)
- call cancel_delayed_work_sync() after the session is closed

## References
- https://git.kernel.org/stable/c/1177afeca833174ba83504688eec898c6214f4bf
- https://git.kernel.org/stable/c/20cf67dcb7db842f941eff1af6ee5e9dc41796d7
- https://git.kernel.org/stable/c/2d33654d40a05afd91ab24c9a73ab512a0670a9a
- https://git.kernel.org/stable/c/33d38c5da17f8db2d80e811b7829d2822c10625e
- https://git.kernel.org/stable/c/34b76d1922e41da1fa73d43b764cddd82ac9733c
- https://git.kernel.org/stable/c/63e5d035e3a7ab7412a008f202633c5e6a0a28ea
- https://git.kernel.org/stable/c/69c7b2fe4c9cc1d3b1186d1c5606627ecf0de883
- https://git.kernel.org/stable/c/9525af1f58f67df387768770fcf6d6a8f23aee3d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42232.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
