# [H] CVE-2017-1000485

## Summary
Severity: High
Advisory: CVE-2017-1000485
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000485
Type: osv

## Details
Nylas Mail Lives 2.2.2 uses 0755 permissions for $HOME/.nylas-mail, which allows local users to obtain sensitive authentication information via standard filesystem operations.

## References
- https://github.com/nylas-mail-lives/nylas-mail/issues/181
