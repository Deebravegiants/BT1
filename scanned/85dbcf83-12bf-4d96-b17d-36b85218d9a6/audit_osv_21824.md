# [H] CVE-2021-46854

## Summary
Severity: High
Advisory: CVE-2021-46854
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2021-46854
Type: osv

## Details
mod_radius in ProFTPD before 1.3.7c allows memory disclosure to RADIUS servers because it copies blocks of 16 characters.

## References
- http://www.proftpd.org/docs/RELEASE_NOTES-1.3.7e
- https://github.com/proftpd/proftpd/pull/1285
- https://security.gentoo.org/glsa/202305-03
- https://bugs.gentoo.org/811495
- https://github.com/proftpd/proftpd/issues/1284
