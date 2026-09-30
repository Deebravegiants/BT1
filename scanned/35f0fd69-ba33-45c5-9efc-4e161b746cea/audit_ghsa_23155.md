# [M] Improper Input Validation in Bouncy Castle

## Summary
Severity: Medium
Advisory: GHSA-8353-fgcr-xfhx
CVE: CVE-2013-1624
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8353-fgcr-xfhx
Type: github-advisory

## Affected
- Maven: `org.bouncycastle:bcprov-jdk15on` — affected >=0 <1.48

## Details
The TLS implementation in the Bouncy Castle Java library before 1.48 and C# library before 1.8 does not properly consider timing side-channel attacks on a noncompliant MAC check operation during the processing of malformed CBC padding, which allows remote attackers to conduct distinguishing attacks and plaintext-recovery attacks via statistical analysis of timing data for crafted packets, a related issue to CVE-2013-0169.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1624
- http://openwall.com/lists/oss-security/2013/02/05/24
- http://rhn.redhat.com/errata/RHSA-2014-0371.html
- http://rhn.redhat.com/errata/RHSA-2014-0372.html
- http://secunia.com/advisories/57716
- http://secunia.com/advisories/57719
- http://www.isg.rhul.ac.uk/tls/TLStiming.pdf
