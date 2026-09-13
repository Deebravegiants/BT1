# [H] Mercurial Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-9xv4-r2hf-26gh
CVE: CVE-2018-13346
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9xv4-r2hf-26gh
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <4.6.1

## Details
The `mpatch_apply` function in `mpatch.c` in Mercurial before 4.6.1 incorrectly proceeds in cases where the fragment start is past the end of the original data, aka OVE-20180430-0004.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13346
- https://access.redhat.com/errata/RHSA-2019:2276
- https://github.com/pypa/advisory-database/tree/main/vulns/mercurial/PYSEC-2018-88.yaml
- https://lists.debian.org/debian-lts-announce/2020/07/msg00032.html
- https://www.mercurial-scm.org/repo/hg/rev/faa924469635
- https://www.mercurial-scm.org/wiki/WhatsNew#Mercurial_4.6.1_.282018-06-06.29
