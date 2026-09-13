# [H] CVE-2019-20387

## Summary
Severity: High
Advisory: CVE-2019-20387
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-20387
Type: osv

## Details
repodata_schema2id in repodata.c in libsolv before 0.7.6 has a heap-based buffer over-read via a last schema whose length is less than the length of the input schema.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00034.html
- https://github.com/openSUSE/libsolv/commit/fdb9c9c03508990e4583046b590c30d958f272da
- https://github.com/openSUSE/libsolv/compare/0.7.5...0.7.6
