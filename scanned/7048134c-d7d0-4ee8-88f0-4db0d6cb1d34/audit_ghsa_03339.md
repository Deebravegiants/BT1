# [M] Forced Browsing in Twisted

## Summary
Severity: Medium
Advisory: GHSA-3gqj-cmxr-p4x2
CVE: CVE-2016-1000111
CWE: CWE-425
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-3gqj-cmxr-p4x2
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0 <16.3.1

## Details
Twisted before 16.3.1 does not attempt to address RFC 3875 section 4.1.18 namespace conflicts and therefore does not protect CGI applications from the presence of untrusted client data in the `HTTP_PROXY` environment variable, which might allow remote attackers to redirect a CGI application's outbound HTTP traffic to an arbitrary proxy server via a crafted Proxy header in an HTTP request, aka an `httpoxy` issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000111
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2020-214.yaml
- https://github.com/twisted/twisted
- https://twistedmatrix.com/pipermail/twisted-web/2016-August/005268.html
- https://twistedmatrix.com/trac/ticket/8623
- https://www.openwall.com/lists/oss-security/2016/07/18/6
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
