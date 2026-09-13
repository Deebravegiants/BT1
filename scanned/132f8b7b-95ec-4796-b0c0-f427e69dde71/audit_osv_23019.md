# [C] CVE-2022-42039

## Summary
Severity: Critical
Advisory: CVE-2022-42039
Aliases: PYSEC-2022-43027, PYSEC-2022-43037
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-42039
Type: osv

## Details
The d8s-lists package for Python, as distributed on PyPI, included a potential code-execution backdoor inserted by a third party. The backdoor is the democritus-dicts package. The affected version is 0.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42039.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42039
- https://github.com/democritus-project/d8s-lists/issues/18
- https://pypi.org/project/d8s-lists/
- https://pypi.org/project/democritus-dicts/
