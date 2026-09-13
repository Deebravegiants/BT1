# [H] Broken Access Control in Canonical LXD DevLXD API

## Summary
Severity: High
Advisory: CVE-2026-12411
Aliases: GHSA-hhf9-qw4v-72xp
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-12411
Type: osv

## Details
Broken Access Control in the devLXDInstancePatchHandler component of Canonical LXD allows an untrusted guest to mount, read, and overwrite another guest's custom storage volume via a crafted device PATCH request over /dev/lxd when security.devlxd.management.volumes is enabled.

## References
- https://github.com/canonical
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12411.json
- https://github.com/canonical/lxd/security/advisories/GHSA-hhf9-qw4v-72xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-12411
- https://github.com/canonical/lxd/pull/18585
- https://github.com/canonical/lxd
