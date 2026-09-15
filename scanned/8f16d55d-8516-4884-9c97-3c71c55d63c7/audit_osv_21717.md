# [H] CVE-2021-45927

## Summary
Severity: High
Advisory: CVE-2021-45927
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45927
Type: osv

## Details
MDB Tools (aka mdbtools) 0.9.2 has a stack-based buffer overflow (at 0x7ffd6e029ee0) in mdb_numeric_to_string (called from mdb_xfer_bound_data and _mdb_attempt_bind).

## References
- https://security.gentoo.org/glsa/202208-12
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=36187
- https://github.com/mdbtools/mdbtools/commit/373b7ff4c4daf887269c078407cb1338942c4ea6
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/mdbtools/OSV-2021-1003.yaml
