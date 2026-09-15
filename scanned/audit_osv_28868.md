# [H] Private npm registry support used scope auth token for downloading tarballs

## Summary
Severity: High
Advisory: CVE-2024-37150
Aliases: GHSA-rfc6-h225-3vxv
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-37150
Type: osv

## Details
An issue in `.npmrc` support in Deno 1.44.0 was discovered where Deno would send `.npmrc` credentials for the scope to the tarball URL when the registry provided URLs for a tarball on a different domain. All users relying on .npmrc are potentially affected by this vulnerability if their private registry references tarball URLs at a different domain. This includes usage of deno install subcommand, auto-install for npm: specifiers and LSP usage. It is recommended to upgrade to Deno 1.44.1 and if your private registry ever serves tarballs at a different domain to rotate your registry credentials.

## References
- https://github.com/npm/cli/wiki/%22No-auth-for-URI,-but-auth-present-for-scoped-registry%22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37150.json
- https://github.com/denoland/deno/security/advisories/GHSA-rfc6-h225-3vxv
- https://nvd.nist.gov/vuln/detail/CVE-2024-37150
- https://github.com/denoland/deno/commit/566adb7c0a0c0845e90a6e867a2c0ef5d2ada575
