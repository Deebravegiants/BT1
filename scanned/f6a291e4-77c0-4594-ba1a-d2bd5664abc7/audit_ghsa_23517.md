# [M] SimpleGeo python-oauth2 vulnerable to the use of Insufficiently Random Values to generate nonces

## Summary
Severity: Medium
Advisory: GHSA-rv8h-p43r-4x5r
CVE: CVE-2013-4347
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rv8h-p43r-4x5r
Type: github-advisory

## Affected
- PyPI: `oauth2` — affected >=0 <1.9rc1

## Details
The (1) make_nonce, (2) generate_nonce, and (3) generate_verifier functions in SimpleGeo python-oauth2 uses weak random numbers to generate nonces, which makes it easier for remote attackers to guess the nonce via a brute force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4347
- https://github.com/simplegeo/python-oauth2/issues/9
- https://github.com/simplegeo/python-oauth2/pull/146
- https://github.com/joestump/python-oauth2/commit/82dd2cdd4954cd7b8983d5d64c0dfd9072bf4650
- https://access.redhat.com/errata/RHSA-2015:1591
- https://access.redhat.com/errata/RHSA-2015:1592
- https://access.redhat.com/security/cve/CVE-2013-4347
- https://bugzilla.redhat.com/show_bug.cgi?id=1007758
- https://github.com/joestump/python-oauth2
- https://github.com/pypa/advisory-database/tree/main/vulns/oauth2/PYSEC-2014-86.yaml
- http://www.openwall.com/lists/oss-security/2013/09/12/7
- http://www.securityfocus.com/bid/62388
