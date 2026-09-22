# [H] Arbitrary File Overwrite in fstream

## Summary
Severity: High
Advisory: GHSA-xf7w-r453-m56c
CVE: CVE-2019-13173
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-xf7w-r453-m56c
Type: github-advisory

## Affected
- npm: `fstream` — affected >=0 <1.0.12

## Details
Versions of `fstream` prior to 1.0.12 are vulnerable to Arbitrary File Overwrite. Extracting tarballs containing a hardlink to a file that already exists in the system and a file that matches the hardlink will overwrite the system's file with the contents of the extracted file. The `fstream.DirWriter()` function is vulnerable.


## Recommendation

Upgrade to version 1.0.12 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13173
- https://github.com/npm/fstream/commit/6a77d2fa6e1462693cf8e46f930da96ec1b0bb22
- https://usn.ubuntu.com/4123-1
- https://www.npmjs.com/advisories/886
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00052.html
