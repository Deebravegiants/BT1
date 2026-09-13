# [C] util-linux libmount Privilege Escalation via Failed Mount Helper

## Summary
Severity: Critical
Advisory: CVE-2026-76642
Aliases: GHSA-m25x-3hj9-m26f
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-76642
Type: osv

## Details
util-linux versions through 2.41.5 and 2.42.2 fail to check mount helper exit status before running post-mount hooks, allowing unprivileged users to execute privileged operations on pre-existing filesystems. Attackers can exploit X-mount.idmap or X-mount.owner hooks to clone filesystems with inherited suid bits or modify target inode permissions after a helper fails, achieving privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76642.json
- https://github.com/util-linux/util-linux/security/advisories/GHSA-m25x-3hj9-m26f
- https://nvd.nist.gov/vuln/detail/CVE-2026-76642
- https://www.vulncheck.com/advisories/util-linux-libmount-privilege-escalation-via-failed-mount-helper
- https://github.com/util-linux/util-linux/commit/1d14676ea70003e9f5b2a6a76af0cadb1190411a
- https://github.com/util-linux/util-linux/commit/a15c00a9e545aa8b9cf6ec0f888ff6c7b3eaeedc
- https://github.com/util-linux/util-linux/commit/f57cea130839c0af8dc0525274267ae4cfd66bbf
- https://github.com/util-linux/util-linux
- https://github.com/util-linux/util-linux/blob/v2.42.2/libmount/src/context_mount.c#L476
- https://github.com/util-linux/util-linux/blob/v2.42.2/libmount/src/context_mount.c#L892
