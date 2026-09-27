# [C] CVE-2017-1000215

## Summary
Severity: Critical
Advisory: CVE-2017-1000215
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000215
Type: osv

## Details
ROOT xrootd version 4.6.0 and below is vulnerable to an unauthenticated shell command injection resulting in remote code execution

## References
- https://github.com/xrootd/xrootd/blob/befa2e627a5a33a38c92db3e57c07d8246a24acf/src/XrdSecgsi/XrdSecgsiGMAPFunLDAP.cc#L85
- https://github.com/xrootd/xrootd/blob/v4.6.1/docs/ReleaseNotes.txt
- https://security.gentoo.org/glsa/201903-11
- https://github.com/xrootd/xrootd/commit/befa2e627a5a33a38c92db3e57c07d8246a24acf
