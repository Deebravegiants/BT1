# [C] HTTP/2 DoS Attacks: Ping, Reset, and Settings Floods

## Summary
Severity: Critical
Advisory: GHSA-32gv-6cf3-wcmq
Ecosystem: PyPI
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-32gv-6cf3-wcmq
Type: github-advisory

## Affected
- PyPI: `twisted` — affected >=0 <19.10.0

## Details
### Impact
Twisted web servers that utilize the optional HTTP/2 support suffer from the following flow-control related vulnerabilities:

Ping flood: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9512
Reset flood: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9514
Settings flood: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-9515

A Twisted web server supports HTTP/2 requests if you've installed the [`http2` optional dependency set](https://twistedmatrix.com/documents/19.2.0/installation/howto/optional.html).

### Workarounds
There are no workarounds.

### References
https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-002.md

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Twisted's Trac](https://twistedmatrix.com/trac/)

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-32gv-6cf3-wcmq
- https://github.com/twisted/twisted/commit/a40ab1ce5210f231abe7a448a54d7e88e48f2d5d
- https://github.com/twisted/twisted
