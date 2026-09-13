# [H] Gentoo Portage does not verify X.509 certificates from SSL servers

## Summary
Severity: High
Advisory: GHSA-8823-xphr-qw9v
CVE: CVE-2013-2100
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8823-xphr-qw9v
Type: github-advisory

## Affected
- PyPI: `portage` — affected >=0 <2.1.12.2

## Details
The urlopen function in pym/portage/util/_urlopen.py in Gentoo Portage 2.1.12, when using HTTPS, does not verify X.509 certificates from SSL servers, which allows man-in-the-middle attackers to spoof servers and modify binary package lists via a crafted certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2100
- https://bugs.gentoo.org/show_bug.cgi?id=469888
- https://exchange.xforce.ibmcloud.com/vulnerabilities/84315
- https://github.com/gentoo/portage
- https://github.com/pypa/advisory-database/tree/main/vulns/portage/PYSEC-2014-115.yaml
- https://security.gentoo.org/glsa/201507-16
- http://openwall.com/lists/oss-security/2013/05/15/5
- http://openwall.com/lists/oss-security/2013/05/16/3
