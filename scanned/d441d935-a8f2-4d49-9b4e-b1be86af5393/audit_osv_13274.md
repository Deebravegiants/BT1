# [H] CVE-2018-19045

## Summary
Severity: High
Advisory: CVE-2018-19045
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-11-08
Source: https://osv.dev/vulnerability/CVE-2018-19045
Type: osv

## Details
keepalived 2.0.8 used mode 0666 when creating new temporary files upon a call to PrintData or PrintStats, potentially leaking sensitive information.

## References
- https://security.gentoo.org/glsa/201903-01
- https://bugzilla.suse.com/show_bug.cgi?id=1015141
- https://github.com/acassen/keepalived/commit/5241e4d7b177d0b6f073cfc9ed5444bf51ec89d6
- https://github.com/acassen/keepalived/commit/c6247a9ef2c7b33244ab1d3aa5d629ec49f0a067
- https://github.com/acassen/keepalived/issues/1048
