# [M] Twisted CRLF Injection

## Summary
Severity: Medium
Advisory: GHSA-6cc5-2vg4-cc7m
CVE: CVE-2019-12387
CWE: CWE-74, CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-10
Source: https://github.com/advisories/GHSA-6cc5-2vg4-cc7m
Type: github-advisory

## Affected
- PyPI: `twisted` — affected >=0 <19.2.1

## Details
In Twisted before 19.2.1, twisted.web did not validate or sanitize URIs or HTTP methods, allowing an attacker to inject invalid characters such as CRLF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12387
- https://github.com/twisted/twisted/commit/6c61fc4503ae39ab8ecee52d10f10ee2c371d7e2
- https://github.com/advisories/GHSA-6cc5-2vg4-cc7m
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2019-128.yaml
- https://github.com/twisted/twisted
- https://labs.twistedmatrix.com/2019/06/twisted-1921-released.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2G5RPDQ4BNB336HL6WW5ZJ344MAWNN7N
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2G5RPDQ4BNB336HL6WW5ZJ344MAWNN7N
- https://twistedmatrix.com/pipermail/twisted-python/2019-June/032352.html
- https://usn.ubuntu.com/4308-1
- https://usn.ubuntu.com/4308-2
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00042.html
