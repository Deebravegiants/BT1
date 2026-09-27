# [M] ePA 3.x Integration: HTTP Header Injection in VAU Inner Requests

## Summary
Severity: Medium
Advisory: CVE-2026-50576
Aliases: GHSA-j8jg-7fqf-4xx9
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50576
Type: osv

## Details
ePA 3.x Integration implements the authorization workflow and writes Medical Information Objects to Germany's electronic patient record. Prior to 1.3.0, ePA 3.x Integration does not neutralize CRLF characters in values used by app/vau/VAUProtokoll.py to construct VAU inner HTTP requests. The build_inner_header function interpolates the uri, host, accept_type, content_type, content_length, USER_AGENT, and insurant_id values into request lines and headers, including x-useragent and x-insurantid. An authenticated attacker who controls a value can inject additional headers into the inner request. Depending on ePA server handling, an injected x-insurantid header can expose another patient's records, and injected Authorization headers can bypass the intended authentication or authorization context. Session-derived USER_AGENT input can also poison requests across the session. This issue is fixed in version 1.3.0.

## References
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/releases/tag/1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50576.json
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/security/advisories/GHSA-j8jg-7fqf-4xx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-50576
- https://www.machinespirits.de/advisory/013a60
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/commit/b984d15d261423302de337adae25e84c54e9c2d1
- https://github.com/fbeta-GmbH/ePA3-Service-OpenSource/pull/11
