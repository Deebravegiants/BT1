# [H] mastercactapus proxyprotocol vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-85c5-ccm8-vr96
CVE: CVE-2019-14243
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-85c5-ccm8-vr96
Type: github-advisory

## Affected
- Go: `github.com/mastercactapus/proxyprotocol` — affected >=0 <0.0.2

## Details
headerv2.go in mastercactapus proxyprotocol before 0.0.2, as used in the mastercactapus caddy-proxyprotocol plugin through 0.0.2 for Caddy, allows remote attackers to cause a denial of service (webserver panic and daemon crash) via a crafted HAProxy PROXY v2 request with truncated source/destination address data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14243
- https://github.com/mastercactapus/caddy-proxyprotocol/issues/8
- https://github.com/mastercactapus/proxyprotocol/issues/1
- https://github.com/mastercactapus/proxyprotocol/commit/5c4a101121fc3e868026189c7a73f7f19eef90ac
- https://caddy.community/t/dos-in-http-proxyprotocol-plugin/6014
- https://github.com/mastercactapus/proxyprotocol
- https://github.com/mastercactapus/proxyprotocol/compare/ef496d7...5c4a101
- https://github.com/mastercactapus/proxyprotocol/releases/tag/v0.0.2
