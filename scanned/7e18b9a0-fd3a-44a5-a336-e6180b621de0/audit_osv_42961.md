# [H] batman-adv: mcast: avoid OOB read of num_dests header

## Summary
Severity: High
Advisory: CVE-2026-72227
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72227
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: mcast: avoid OOB read of num_dests header

Before the access to struct batadv_tvlv_mcast_tracker's num_dests, it is
attempted to check whether enough space is actually in the network header.
But instead of using offsetofend() to check for the whole size (2) which
must be accessible, offsetof() of is called. The latter is always returning
0. The comparison with the network header length will always return that
enough data is available - even when only 1 or 0 bytes are accessible.

Instead of using offsetofend(), use the more common check for the whole
header.

## References
- https://git.kernel.org/stable/c/38eaed28e250895d56f4b7989bd65479a511c5c3
- https://git.kernel.org/stable/c/7d1a877670bc2e901241073f022ca8d1b2f85f1c
- https://git.kernel.org/stable/c/80f62893d135f415e7a374dd47b468ec298f7aed
- https://git.kernel.org/stable/c/d2b657c9653fcebca828a2ead13f444e0da68817
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72227.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
