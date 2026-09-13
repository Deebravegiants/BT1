# [C] CVE-2022-41387

## Summary
Severity: Critical
Advisory: CVE-2022-41387
Aliases: PYSEC-2022-43029, PYSEC-2022-43050
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-41387
Type: osv

## Details
The d8s-pdfs package for Python, as distributed on PyPI, included a potential code-execution backdoor inserted by a third party. The backdoor is the democritus-urls package. The affected version is 0.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41387.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41387
- https://github.com/democritus-project/d8s-pdfs/issues/7
- https://pypi.org/project/d8s-pdfs/
- https://pypi.org/project/democritus-urls/
