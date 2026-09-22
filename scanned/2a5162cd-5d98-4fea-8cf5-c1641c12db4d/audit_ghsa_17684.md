# [H] tar-fs can extract outside the specified dir with a specific tarball

## Summary
Severity: High
Advisory: GHSA-8cj5-5rvv-wf4v
CVE: CVE-2025-48387
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-03
Source: https://github.com/advisories/GHSA-8cj5-5rvv-wf4v
Type: github-advisory

## Affected
- npm: `tar-fs` — affected >=0 <1.16.5
- npm: `tar-fs` — affected >=2.0.0 <2.1.3
- npm: `tar-fs` — affected >=3.0.0 <3.0.9

## Details
### Impact
 v3.0.8, v2.1.2, v1.16.4 and below

### Patches
Has been patched in 3.0.9, 2.1.3, and 1.16.5

### Workarounds
You can use the ignore option to ignore non files/directories.

```js
  ignore (_, header) {
    // pass files & directories, ignore e.g. symlinks
    return header.type !== 'file' && header.type !== 'directory'
  }
```

### Credit
Thank you Caleb Brown from Google Open Source Security Team for reporting this in detail.

## References
- https://github.com/google/security-research/security/advisories/GHSA-xrg4-qp5w-2c3w
- https://github.com/mafintosh/tar-fs/security/advisories/GHSA-8cj5-5rvv-wf4v
- https://nvd.nist.gov/vuln/detail/CVE-2025-48387
- https://github.com/mafintosh/tar-fs/commit/647447b572bc135c41035e82ca7b894f02b17f0f
- https://github.com/mafintosh/tar-fs
- https://lists.debian.org/debian-lts-announce/2025/06/msg00012.html
