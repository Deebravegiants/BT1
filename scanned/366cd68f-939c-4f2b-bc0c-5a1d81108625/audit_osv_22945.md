# [C] CVE-2022-41384

## Summary
Severity: Critical
Advisory: CVE-2022-41384
Aliases: PYSEC-2022-43023, PYSEC-2022-43047
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-41384
Type: osv

## Details
The d8s-domains package for Python, as distributed on PyPI, included a potential code-execution backdoor inserted by a third party. The backdoor is the democritus-urls package. The affected version is 0.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41384.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41384
- https://github.com/democritus-project/d8s-domains/issues/9
- https://pypi.org/project/d8s-domains/
- https://pypi.org/project/democritus-urls/
