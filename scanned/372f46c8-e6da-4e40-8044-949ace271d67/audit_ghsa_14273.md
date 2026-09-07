# [M] Path Traversal in Asset "import from server" option

## Summary
Severity: Medium
Advisory: GHSA-hg77-vx9v-f49x
CVE: CVE-2023-2336
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-hg77-vx9v-f49x
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
An authenticated attacker can abuse import-server-files with a path traversal to download an arbitrary file from the server

An arbitrary file read vulnerability allows an attacker to read files on the server that they should not have access to, potentially including sensitive files such as configuration files, user data, and credentials. This can result in the exposure of confidential information, which can be used to launch further attacks or compromise the system.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/498cadec2292f7842fb10612068ac78496e884b4.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/498cadec2292f7842fb10612068ac78496e884b4.patch manually.

### References
https://huntr.dev/bounties/af764624-7746-4f53-8480-85348dbb4f14/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-hg77-vx9v-f49x
- https://nvd.nist.gov/vuln/detail/CVE-2023-2336
- https://github.com/pimcore/pimcore/commit/498cadec2292f7842fb10612068ac78496e884b4
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/af764624-7746-4f53-8480-85348dbb4f14
