# [M] CVE-2018-17828

## Summary
Severity: Medium
Advisory: CVE-2018-17828
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-10-01
Source: https://osv.dev/vulnerability/CVE-2018-17828
Type: osv

## Details
Directory traversal vulnerability in ZZIPlib 0.13.69 allows attackers to overwrite arbitrary files via a .. (dot dot) in a zip file, because of the function unzzip_cat in the bins/unzzipcat-mem.c file.

## References
- https://github.com/gdraheim/zziplib/issues/62
