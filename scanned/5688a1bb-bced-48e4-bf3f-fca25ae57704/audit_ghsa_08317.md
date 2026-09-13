# [H] OpenStack Swift: s3api middleware enters an infinite loop when processing a truncated aws-chunked PUT request body

## Summary
Severity: High
Advisory: GHSA-g7jq-j257-rww2
CVE: CVE-2026-49017
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-g7jq-j257-rww2
Type: github-advisory

## Affected
- PyPI: `swift` — affected >=2.36.0
- PyPI: `swift` — affected >=2.37.0

## Details
In OpenStack Swift before 2.36.2 and 2.37.2, s3api middleware enters an infinite loop when processing a truncated aws-chunked PUT request body. The StreamingInput class repeatedly appends an empty buffer and re-reads, causing the proxy-server worker handling the request to become permanently unresponsive with increasing CPU and memory consumption. An authenticated attacker can systematically exhaust all proxy-server workers, resulting in denial of service. The defect was introduced in Swift 2.36.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49017
- https://bugs.launchpad.net/bugs/2152205
- https://github.com/openstack/swift
- https://review.opendev.org/c/openstack/swift/+/987957
- https://review.opendev.org/c/openstack/swift/+/988093
- http://www.openwall.com/lists/oss-security/2026/05/27/9
- http://www.openwall.com/lists/oss-security/2026/06/02/6
