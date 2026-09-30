# [M] Pydantic regular expression denial of service

## Summary
Severity: Medium
Advisory: GHSA-mr82-8j83-vxmv
CVE: CVE-2024-3772
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-mr82-8j83-vxmv
Type: github-advisory

## Affected
- PyPI: `pydantic` — affected >=2.0.0 <2.4.0
- PyPI: `pydantic` — affected >=0 <1.10.13

## Details
Regular expression denial of service in Pydantic < 2.4.0, < 1.10.13 allows remote attackers to cause denial of service via a crafted email string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3772
- https://github.com/pydantic/pydantic/pull/7360
- https://github.com/pydantic/pydantic/commit/59d8f38fd6220e3917c53785dbc70317d6f8e631
- https://github.com/pydantic/pydantic/commit/e4393ae6145c4dadff739990bb0116c6dec3441b
- https://github.com/pydantic/pydantic
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6JBZLMSH4GAZOVBMT2JUO2LXHY7M2ALI
