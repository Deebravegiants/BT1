# [H] Twisted SSH client and server deny of service during SSH handshake.

## Summary
Severity: High
Advisory: GHSA-rv6r-3f5q-9rgx
CVE: CVE-2022-21716
CWE: CWE-120, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-03
Source: https://github.com/advisories/GHSA-rv6r-3f5q-9rgx
Type: github-advisory

## Affected
- PyPI: `twisted` — affected >=21.7.0 <22.2.0

## Details
### Impact

The Twisted SSH client and server implementation naively accepted an infinite amount of data for the  peer's SSH version identifier.

A malicious peer can trivially craft a request that uses all available memory and crash the server, resulting in denial of service. The attack is as simple as `nc -rv localhost 22 < /dev/zero`.

### Patches

The issue was fix in GitHub commit https://github.com/twisted/twisted/commit/98387b39e9f0b21462f6abc7a1325dc370fcdeb1

A fix is available in Twisted 22.2.0.

### Workarounds

* Limit access to the SSH server only to trusted source IP addresses.
* Connect over SSH only to trusted destination IP addresses.

### References

Reported at https://twistedmatrix.com/trac/ticket/10284
Discussions at https://github.com/twisted/twisted/security/advisories/GHSA-rv6r-3f5q-9rgx

### For more information

Found by vin01

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-rv6r-3f5q-9rgx
- https://nvd.nist.gov/vuln/detail/CVE-2022-21716
- https://github.com/twisted/twisted/commit/89c395ee794e85a9657b112c4351417850330ef9
- https://github.com/twisted/twisted/commit/98387b39e9f0b21462f6abc7a1325dc370fcdeb1
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2022-160.yaml
- https://github.com/twisted/twisted
- https://github.com/twisted/twisted/releases/tag/twisted-22.2.0
- https://lists.debian.org/debian-lts-announce/2022/03/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7U6KYDTOLPICAVSR34G2WRYLFBD2YW5K
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GLKHA6WREIVAMBQD7KKWYHPHGGNKMAG6
- https://security.gentoo.org/glsa/202301-02
- https://twistedmatrix.com/trac/ticket/10284
- https://www.oracle.com/security-alerts/cpuapr2022.html
