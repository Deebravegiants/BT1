# [H] tar-fs has a symlink validation bypass if destination directory is predictable with a specific tarball

## Summary
Severity: High
Advisory: GHSA-vj76-c3g6-qr5v
CVE: CVE-2025-59343
CWE: CWE-22, CWE-61
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-vj76-c3g6-qr5v
Type: github-advisory

## Affected
- npm: `tar-fs` — affected >=3.0.0 <3.1.1
- npm: `tar-fs` — affected >=2.0.0 <2.1.4
- npm: `tar-fs` — affected >=0 <1.16.6

## Details
### Impact
 v3.1.0, v2.1.3, v1.16.5 and below

### Patches
Has been patched in 3.1.1, 2.1.4, and 1.16.6

### Workarounds
You can use the ignore option to ignore non files/directories.

```js
  ignore (_, header) {
    // pass files & directories, ignore e.g. symlinks
    return header.type !== 'file' && header.type !== 'directory'
  }
```

### Credit
Reported by: Mapta / BugBunny_ai

## References
- https://github.com/mafintosh/tar-fs/security/advisories/GHSA-vj76-c3g6-qr5v
- https://nvd.nist.gov/vuln/detail/CVE-2025-59343
- https://github.com/mafintosh/tar-fs/commit/0bd54cdf06da2b7b5b95cd4b062c9f4e0a8c4e09
- https://github.com/mafintosh/tar-fs
- https://lists.debian.org/debian-lts-announce/2025/09/msg00028.html
