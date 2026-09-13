# [H] `Cookie` HTTP header isn't stripped on cross-origin redirects

## Summary
Severity: High
Advisory: GHSA-v845-jxx5-vc9f
CVE: CVE-2023-43804
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-10-02
Source: https://github.com/advisories/GHSA-v845-jxx5-vc9f
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=2.0.0 <2.0.6
- PyPI: `urllib3` — affected >=0 <1.26.17

## Details
urllib3 doesn't treat the `Cookie` HTTP header special or provide any helpers for managing cookies over HTTP, that is the responsibility of the user. However, it is possible for a user to specify a `Cookie` header and unknowingly leak information via HTTP redirects to a different origin if that user doesn't disable redirects explicitly.

Users **must** handle redirects themselves instead of relying on urllib3's automatic redirects to achieve safe processing of the `Cookie` header, thus we decided to strip the header by default in order to further protect users who aren't using the correct approach.

## Affected usages

We believe the number of usages affected by this advisory is low. It requires all of the following to be true to be exploited:

* Using an affected version of urllib3 (patched in v1.26.17 and v2.0.6)
* Using the `Cookie` header on requests, which is mostly typical for impersonating a browser.
* Not disabling HTTP redirects
* Either not using HTTPS or for the origin server to redirect to a malicious origin.

## Remediation

* Upgrading to at least urllib3 v1.26.17 or v2.0.6
* Disabling HTTP redirects using `redirects=False` when sending requests.
* Not using the `Cookie` header.

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-v845-jxx5-vc9f
- https://nvd.nist.gov/vuln/detail/CVE-2023-43804
- https://github.com/urllib3/urllib3/commit/01220354d389cd05474713f8c982d05c9b17aafb
- https://github.com/urllib3/urllib3/commit/644124ecd0b6e417c527191f866daa05a5a2056d
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2023-192.yaml
- https://github.com/urllib3/urllib3
- https://lists.debian.org/debian-lts-announce/2023/10/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5F5CUBAN5XMEBVBZPHFITBLMJV5FIJJ5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I3PR7C6RJ6JUBQKIJ644DMIJSUP36VDY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NDAGZXYJ7H2G3SB47M453VQVNAWKAEJJ
- https://security.netapp.com/advisory/ntap-20241213-0007
- https://www.vicarius.io/vsociety/posts/cve-2023-43804-urllib3-vulnerability-3
