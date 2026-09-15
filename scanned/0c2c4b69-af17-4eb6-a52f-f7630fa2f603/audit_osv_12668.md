# [M] CVE-2018-14329

## Summary
Severity: Medium
Advisory: CVE-2018-14329
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14329
Type: osv

## Details
In HTSlib 1.8, a race condition in cram/cram_io.c might allow local users to overwrite arbitrary files via a symlink attack.

## References
- https://github.com/samtools/htslib/issues/736
