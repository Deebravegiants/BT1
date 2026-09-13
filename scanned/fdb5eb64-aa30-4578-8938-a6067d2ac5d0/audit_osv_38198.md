# [M] deepinid plugin in dde-control-center is configured to skip TLS certificate verification when downloading avatar from remote server

## Summary
Severity: Medium
Advisory: CVE-2026-35207
Aliases: GHSA-jf2h-4vqc-3jgc
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-35207
Type: osv

## Details
dde-control-center is the control panel of DDE, the Deepin Desktop Environment. plugin-deepinid is a plugin in dde-control-center, which provides the deepinid cloud service. Prior to 6.1.80, plugin-deepinid is configured to skip TLS certificate verification when fetching the user's avatar from openapi.deepin.com or other providers. An MITM attacker could intercept the traffic, replace the avatar with a malicious or misleading image, and potentially identify the user by the avatar. This vulnerability is fixed in dde-control-center 6.1.80 and 5.9.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35207.json
- https://github.com/linuxdeepin/developer-center/security/advisories/GHSA-jf2h-4vqc-3jgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35207
- https://github.com/linuxdeepin/dde-control-center/commit/6fc206120be28d9eef7d72258662bcabb834367f
- https://github.com/linuxdeepin/dde-control-center/commit/cd95b054ff10a35bc9284431631305bd56244b3d
- https://github.com/linuxdeepin/dde-control-center/pull/3146
