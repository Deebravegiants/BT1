# [H] AMPHP Denial of Service via HTTP/2 CONTINUATION Frames

## Summary
Severity: High
Advisory: GHSA-qjfw-cvjf-f4fm
CVE: CVE-2024-2653
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-qjfw-cvjf-f4fm
Type: github-advisory

## Affected
- Packagist: `amphp/http` — affected >=2.0.0 <2.1.1
- Packagist: `amphp/http` — affected >=0 <1.7.3
- Packagist: `amphp/http-client` — affected >=4.0.0-rc10

## Details
`amphp/http` will collect HTTP/2 `CONTINUATION` frames in an unbounded buffer and will not check the header size limit until it has received the `END_HEADERS` flag, resulting in an OOM crash. `amphp/http-client` and `amphp/http-server` are indirectly affected if they're used with an unpatched version of `amphp/http`. Early versions of `amphp/http-client` with HTTP/2 support (v4.0.0-rc10 to 4.0.0) are also directly affected.

## Acknowledgements

Thank you to [Bartek Nowotarski](https://nowotarski.info/) for reporting the vulnerability.

## References
- https://github.com/amphp/http-client/security/advisories/GHSA-w8gf-g2vq-j2f4
- https://github.com/amphp/http/security/advisories/GHSA-qjfw-cvjf-f4fm
- https://nvd.nist.gov/vuln/detail/CVE-2024-2653
- https://github.com/amphp/http/commit/3a33e68a3b53f7279217238e89748cf0cb30b8a6
- https://github.com/amphp/http/commit/881cc33da236fbcd0cb0cf6c2bfc7efcf80ede76
- https://github.com/FriendsOfPHP/security-advisories/blob/master/amphp/http-client/CVE-2024-2653.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/amphp/http/CVE-2024-2653.yaml
- https://github.com/amphp/http
- https://www.kb.cert.org/vuls/id/421644
- http://www.openwall.com/lists/oss-security/2024/04/03/16
