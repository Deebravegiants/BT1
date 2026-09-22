# [H] Mistune vulnerable to catastrophic backtracking

## Summary
Severity: High
Advisory: GHSA-fw3v-x4f2-v673
CVE: CVE-2022-34749
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-fw3v-x4f2-v673
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=2.0.0a1 <2.0.3

## Details
In Mistune through 2.0.2, support of inline markup is implemented by using regular expressions that can involve a high amount of backtracking on certain edge cases. This behavior is commonly named catastrophic backtracking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34749
- https://github.com/lepture/mistune/issues/314#issuecomment-1223972386
- https://github.com/lepture/mistune/commit/a6d43215132fe4f3d93f8d7e90ba83b16a0838b2
- https://github.com/lepture/mistune/commit/ca1e7b506850f4e488823fc7338b49a8f9852718
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2022-237.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TQHXITQ2DSBYOILKHXBSBB7PFBPZHF63
