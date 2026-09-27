# [M] CVE-2015-8927

## Summary
Severity: Medium
Advisory: CVE-2015-8927
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/CVE-2015-8927
Type: osv

## Details
The trad_enc_decrypt_update function in archive_read_support_format_zip.c in libarchive before 3.2.0 allows remote attackers to cause a denial of service (out-of-bounds heap read and crash) via a crafted zip file, related to reading the password.

## References
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://blog.fuzzing-project.org/47-Many-invalid-memory-access-issues-in-libarchive.html
- https://github.com/libarchive/libarchive/issues/523
- https://security.gentoo.org/glsa/201701-03
- http://www.openwall.com/lists/oss-security/2016/06/17/2
- http://www.openwall.com/lists/oss-security/2016/06/17/5
- https://github.com/libarchive/libarchive/issues/523
- https://github.com/libarchive/libarchive/issues/523
- http://www.securityfocus.com/bid/91329
