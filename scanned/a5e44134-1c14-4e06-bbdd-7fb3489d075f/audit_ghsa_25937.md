# [C] Puma vulnerable to HTTP Request Smuggling

## Summary
Severity: Critical
Advisory: GHSA-h99w-9q5r-gjq9
CVE: CVE-2022-24790
CWE: CWE-444
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-h99w-9q5r-gjq9
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=5.0.0 <5.6.4
- RubyGems: `puma` — affected >=0 <4.3.12

## Details
When using Puma behind a proxy that does not properly validate that the incoming HTTP request matches the RFC7230 standard, Puma and the frontend proxy may disagree on where a request starts and ends. This would allow requests to be smuggled via the front-end proxy to Puma.

The following vulnerabilities are addressed by this advisory:
- Lenient parsing of `Transfer-Encoding` headers, when unsupported encodings should be rejected and the final encoding must be `chunked`.
- Lenient parsing of malformed `Content-Length` headers and chunk sizes, when only digits and hex digits should be allowed.
- Lenient parsing of duplicate `Content-Length` headers, when they should be rejected.
- Lenient parsing of the ending of chunked segments, when they should end with `\r\n`.

The vulnerability has been fixed in 5.6.4 and 4.3.12. When deploying a proxy in front of Puma, turning on any and all functionality to make sure that the request matches the RFC7230 standard. 

These proxy servers are known to have "good" behavior re: this standard and upgrading Puma may not be necessary. Users are encouraged to validate for themselves.

- Nginx (latest)
- Apache (latest)
- Haproxy 2.5+
- Caddy (latest)
- Traefik (latest)

## References
- https://github.com/puma/puma/security/advisories/GHSA-h99w-9q5r-gjq9
- https://nvd.nist.gov/vuln/detail/CVE-2022-24790
- https://github.com/puma/puma/commit/5bb7d202e24dec00a898dca4aa11db391d7787a5
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2022-24790.yml
- https://lists.debian.org/debian-lts-announce/2022/08/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F6YWGIIKL7KKTS3ZOAYMYPC7D6WQ5OA5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L7NESIBFCNSR3XH7LXDPKVMSUBNUB43G
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TUBFJ44NCKJ34LECZRAP4N5VL6USJSIB
- https://portswigger.net/web-security/request-smuggling
- https://security.gentoo.org/glsa/202208-28
- https://www.debian.org/security/2022/dsa-5146
