# [M] Advanced permissions not respected when copying entire group folders

## Summary
Severity: Medium
Advisory: CVE-2023-39952
Aliases: GHSA-cq8w-v4fh-4rjq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-10
Source: https://osv.dev/vulnerability/CVE-2023-39952
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 22.0.0 and prior to versions 22.2.10.13, 23.0.12.8, 24.0.12.4, 25.0.8, 26.0.3, and 27.0.1, a user can access files inside a subfolder of a groupfolder accessible to them, even if advanced permissions would block access to the subfolder. Nextcloud Server versions 25.0.8, 26.0.3, and 27.0.1 and Nextcloud Enterprise Server versions 22.2.10.13, 23.0.12.8, 24.0.12.4, 25.0.8, 26.0.3, and 27.0.1 contain a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1808079
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39952.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-cq8w-v4fh-4rjq
- https://nvd.nist.gov/vuln/detail/CVE-2023-39952
- https://github.com/nextcloud/groupfolders/issues/1906
- https://github.com/nextcloud/server/pull/38890
