# [H] Server-Side Request Forgery in Apache Traffic Control

## Summary
Severity: High
Advisory: GHSA-wp47-9r3h-xfgq
CVE: CVE-2022-23206
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-07
Source: https://github.com/advisories/GHSA-wp47-9r3h-xfgq
Type: github-advisory

## Affected
- Go: `github.com/apache/trafficcontrol` — affected >=6.0.0 <6.1.0
- Go: `github.com/apache/trafficcontrol` — affected >=0 <5.1.6

## Details
In Apache Traffic Control Traffic Ops prior to 6.1.0 or 5.1.6, an unprivileged user who can reach Traffic Ops over HTTPS can send a specially-crafted POST request to /user/login/oauth to scan a port of a server that Traffic Ops can reach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23206
- https://lists.apache.org/thread/lsrd2mqj29vrvwsh8g0d560vvz8n126f
