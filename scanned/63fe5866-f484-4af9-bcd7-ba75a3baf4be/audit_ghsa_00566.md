# [H] python-gnupg's shell_quote function does not properly escape characters

## Summary
Severity: High
Advisory: GHSA-2jc8-4r6g-282j
CVE: CVE-2014-1928
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-2jc8-4r6g-282j
Type: github-advisory

## Affected
- PyPI: `python-gnupg` — affected >=0.3.5 <0.3.6

## Details
The shell_quote function in python-gnupg 0.3.5 does not properly escape characters, which allows context-dependent attackers to execute arbitrary code via shell metacharacters in unspecified vectors, as demonstrated using "\" (backslash) characters to form multi-command sequences, a different vulnerability than CVE-2014-1927.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-7323.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1928
- https://code.google.com/p/python-gnupg
- https://code.google.com/p/python-gnupg/issues/detail?id=98
- https://github.com/advisories/GHSA-2jc8-4r6g-282j
- https://github.com/pypa/advisory-database/tree/main/vulns/python-gnupg/PYSEC-2014-91.yaml
- http://seclists.org/oss-sec/2014/q1/246
- http://seclists.org/oss-sec/2014/q1/294
- http://www.debian.org/security/2014/dsa-2946
