# [C] CVE-2022-42038

## Summary
Severity: Critical
Advisory: CVE-2022-42038
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-42038
Type: osv

## Details
The d8s-ip-addresses package for Python, as distributed on PyPI, included a potential code-execution backdoor inserted by a third party. The backdoor is the democritus-csv package. The affected version is 0.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42038.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42038
- https://github.com/democritus-project/d8s-ip-addresses/issues/14
- https://pypi.org/project/d8s-ip-addresses/
- https://pypi.org/project/democritus-csv/
