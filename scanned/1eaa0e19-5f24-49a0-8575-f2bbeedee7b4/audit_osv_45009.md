# [M] Authenticated Denial of Service via Malicious Backup Tarball in LXD

## Summary
Severity: Medium
Advisory: CVE-2026-9639
Aliases: GHSA-j93m-3j9p-m5m8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-9639
Type: osv

## Details
Nil-pointer dereference in CreateCustomVolumeFromBackup in LXD up to version 6.8 and 5.21 on Linux allows an authenticated user with can_create_storage_volumes permissions to cause a denial of service via a specially crafted custom-volume backup tarball that omits the expires_at snapshot field.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9639.json
- https://github.com/canonical/lxd/security/advisories/GHSA-j93m-3j9p-m5m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-9639
- https://github.com/canonical/lxd/pull/18320
- https://github.com/canonical/lxd/pull/18390
- https://github.com/canonical/lxd
