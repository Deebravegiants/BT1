# [H] CVE-2022-40898

## Summary
Severity: High
Advisory: CVE-2022-40898
Aliases: GHSA-qwmp-2cf2-g9g6, PYSEC-2022-43017
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-40898
Type: osv

## Details
An issue discovered in Python Packaging Authority (PyPA) Wheel 0.37.1 and earlier allows remote attackers to cause a denial of service via attacker controlled input to wheel cli.

## References
- https://github.com/pypa/wheel/blob/main/src/wheel/wheelfile.py#L18
- https://pyup.io/posts/pyup-discovers-redos-vulnerabilities-in-top-python-packages/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40898.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40898
- https://pypi.org/project/wheel/
