# [H] Rancher Vulnerable to Cross-site Request Forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-xhg2-rvm8-w2jh
CVE: CVE-2019-13209
CWE: CWE-352, CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-xhg2-rvm8-w2jh
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.0.16
- Go: `github.com/rancher/rancher` — affected >=2.1.0 <2.1.11
- Go: `github.com/rancher/rancher` — affected >=2.2.0 <2.2.5

## Details
Rancher 2 through 2.2.4 is vulnerable to a Cross-Site Websocket Hijacking attack that allows an exploiter to gain access to clusters managed by Rancher. The attack requires a victim to be logged into a Rancher server, and then to access a third-party site hosted by the exploiter. Once that is accomplished, the exploiter is able to execute commands against the cluster's Kubernetes API with the permissions and identity of the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13209
- https://github.com/rancher/rancher/commit/0ddffe484adccb9e37d9432e8e625d8ebbfb0088
- https://forums.rancher.com/t/rancher-release-v2-2-5-addresses-rancher-cve-2019-13209/14801
- https://github.com/rancher/rancher
