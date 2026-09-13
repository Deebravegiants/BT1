# [M] Tweepy does not verify SSL Certificate 

## Summary
Severity: Medium
Advisory: GHSA-pwx5-xg7g-wpc5
CVE: CVE-2012-5825
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pwx5-xg7g-wpc5
Type: github-advisory

## Affected
- PyPI: `tweepy` — affected >=0 <3.0

## Details
Tweepy does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate, related to use of the Python httplib library.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5825
- https://github.com/tweepy/tweepy/issues/279
- https://github.com/tweepy/tweepy/pull/400
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79831
- https://github.com/pypa/advisory-database/tree/main/vulns/tweepy/PYSEC-2012-17.yaml
- https://github.com/tweepy/tweepy
- http://www.cs.utexas.edu/~shmat/shmat_ccs12.pdf
