# [M] CVE-2021-29133

## Summary
Severity: Medium
Advisory: CVE-2021-29133
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/CVE-2021-29133
Type: osv

## Details
Lack of verification in haserl, a component of Alpine Linux Configuration Framework, before 0.9.36 allows local users to read the contents of any file on the filesystem.

## References
- https://twitter.com/steaIth/status/1364940271054712842
- https://gitlab.alpinelinux.org/alpine/aports/-/issues/12539
- https://github.com/rapid7/metasploit-framework/pull/14833
- https://github.com/rapid7/metasploit-framework/pull/14833/commits/5bf6b2d094deb22fa8183ce161b90cbe4fd40a70
