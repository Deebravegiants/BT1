# [H] CVE-2021-40524

## Summary
Severity: High
Advisory: CVE-2021-40524
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-05
Source: https://osv.dev/vulnerability/CVE-2021-40524
Type: osv

## Details
In Pure-FTPd before 1.0.50, an incorrect max_filesize quota mechanism in the server allows attackers to upload files of unbounded size, which may lead to denial of service or a server hang. This occurs because a certain greater-than-zero test does not anticipate an initial -1 value. (Versions 1.0.23 through 1.0.49 are affected.)

## References
- https://lists.debian.org/debian-lts-announce/2025/11/msg00003.html
- https://github.com/jedisct1/pure-ftpd/commit/37ad222868e52271905b94afea4fc780d83294b4
- https://github.com/jedisct1/pure-ftpd/compare/1.0.49...1.0.50
- https://github.com/jedisct1/pure-ftpd/pull/158
