# [H] CVE-2020-29050

## Summary
Severity: High
Advisory: CVE-2020-29050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2020-29050
Type: osv

## Details
SphinxSearch in Sphinx Technologies Sphinx through 3.1.1 allows directory traversal (in conjunction with CVE-2019-14511) because the mysql client can be used for CALL SNIPPETS and load_file operations on a full pathname (e.g., a file in the /etc directory). NOTE: this is unrelated to CMUSphinx.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00009.html
- https://security-tracker.debian.org/tracker/CVE-2020-29050
- https://blog.wirhabenstil.de/2019/08/19/sphinxsearch-0-0-0-09306-cve-2019-14511/
