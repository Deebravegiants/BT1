# [H] Improper Input Validation in XFire

## Summary
Severity: High
Advisory: GHSA-5jc8-8xhv-g8qm
CVE: CVE-2012-5817
CWE: CWE-20, CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5jc8-8xhv-g8qm
Type: github-advisory

## Affected
- Maven: `org.codehaus.xfire:xfire-core` — affected >=0

## Details
Codehaus XFire 1.2.6 and earlier, as used in the Amazon EC2 API Tools Java library and other products, does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5817
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79934
- http://www.cs.utexas.edu/~shmat/shmat_ccs12.pdf
