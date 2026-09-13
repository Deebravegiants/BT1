# [M] Weblate user account enumeration via reset password form

## Summary
Severity: Medium
Advisory: GHSA-j24g-gm76-j829
CVE: CVE-2017-5537
CWE: CWE-200, CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j24g-gm76-j829
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <2.10.1

## Details
The password reset form in Weblate before 2.10.1 provides different error messages depending on whether the email address is associated with an account, which allows remote attackers to enumerate user accounts via a series of requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5537
- https://github.com/WeblateOrg/weblate/issues/1317
- https://github.com/WeblateOrg/weblate/commit/abe0d2a29a1d8e896bfe829c8461bf8b391f1079
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/blob/weblate-2.10.1/docs/changes.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2017-42.yaml
- http://www.openwall.com/lists/oss-security/2017/01/18/11
- http://www.openwall.com/lists/oss-security/2017/01/20/1
- http://www.securityfocus.com/bid/95676
