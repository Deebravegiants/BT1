# [H] pypa/setuptools vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-r9hx-vwmv-q579
CVE: CVE-2022-40897
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-r9hx-vwmv-q579
Type: github-advisory

## Affected
- PyPI: `setuptools` — affected >=0 <65.5.1

## Details
Python Packaging Authority (PyPA)'s setuptools is a library designed to facilitate packaging Python projects. Setuptools version 65.5.0 and earlier could allow remote attackers to cause a denial of service by fetching malicious HTML from a PyPI package or custom PackageIndex page due to a vulnerable Regular Expression in `package_index`. This has been patched in version 65.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40897
- https://github.com/pypa/setuptools/issues/3659
- https://github.com/pypa/setuptools/commit/43a9c9bfa6aa626ec2a22540bea28d2ca77964be
- https://setuptools.pypa.io/en/latest
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.netapp.com/advisory/ntap-20230214-0001
- https://pyup.io/vulnerabilities/CVE-2022-40897/52495
- https://pyup.io/posts/pyup-discovers-redos-vulnerabilities-in-top-python-packages
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YNA2BAH2ACBZ4TVJZKFLCR7L23BG5C3H
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ADES3NLOE5QJKBLGNZNI2RGVOSQXA37R
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YNA2BAH2ACBZ4TVJZKFLCR7L23BG5C3H
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ADES3NLOE5QJKBLGNZNI2RGVOSQXA37R
- https://lists.debian.org/debian-lts-announce/2024/09/msg00018.html
- https://github.com/pypa/setuptools/compare/v65.5.0...v65.5.1
- https://github.com/pypa/setuptools/blob/fe8a98e696241487ba6ac9f91faa38ade939ec5d/setuptools/package_index.py#L200
- https://github.com/pypa/setuptools
- https://github.com/pypa/advisory-database/tree/main/vulns/setuptools/PYSEC-2022-43012.yaml
