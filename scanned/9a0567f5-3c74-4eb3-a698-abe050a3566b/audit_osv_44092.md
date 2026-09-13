# [C] OpenZFS: user-namespace capability check allows unprivileged local authorization bypass

## Summary
Severity: Critical
Advisory: CVE-2026-79619
Aliases: GHSA-mhf5-q8gw-qg9v
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-79619
Type: osv

## Details
On Linux, several OpenZFS ioctl authorization checks accept a capability held only within a user-created, unprivileged namespace as equivalent to real host privilege, allowing an unprivileged local user to perform operations that should require root. Affected operations include pool-administrative operations (eg create, import, destroy), pool event log access (zpool events) and fault injection (zinject). Exploiting the problem requires only that the local user is permitted to open /dev/zfs (governed by local device permissions) and that the kernel permits unprivileged user namespace creation. No prior access to the target pool or its underlying devices is needed.

## References
- https://github.com/openzfs/zfs/releases/tag/zfs-2.2.11
- https://github.com/openzfs/zfs/releases/tag/zfs-2.3.9
- https://github.com/openzfs/zfs/releases/tag/zfs-2.4.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79619.json
- https://github.com/advisories/GHSA-mhf5-q8gw-qg9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-79619
- https://github.com/openzfs/zfs/pull/18959
- https://github.com/openzfs/zfs
- https://seclists.org/fulldisclosure/2026/Aug/40
