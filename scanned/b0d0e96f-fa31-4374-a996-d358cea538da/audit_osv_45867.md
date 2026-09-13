# [M] curl's websocket code did not update the 32 bit mask pattern for each new outgoing frame as the...

## Summary
Severity: Medium
Advisory: JLSEC-2026-423
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-423
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.11.0+0 <8.16.0+0
- Julia: `LibCURL_jll` — affected >=8.11.0+0 <8.16.0+0

## Details
curl's websocket code did not update the 32 bit mask pattern for each new
outgoing frame as the specification says. Instead it used a fixed mask that
persisted and was used throughout the entire connection.

A predictable mask pattern allows for a malicious server to induce traffic
between the two communicating parties that could be interpreted by an involved
proxy (configured or transparent) as genuine, real, HTTP traffic with content
and thereby poison its cache. That cached poisoned content could then be
served to all users of that proxy.

## References
- http://www.openwall.com/lists/oss-security/2025/09/10/2
- http://www.openwall.com/lists/oss-security/2025/09/10/3
- http://www.openwall.com/lists/oss-security/2025/09/10/4
- https://curl.se/docs/CVE-2025-10148.html
- https://curl.se/docs/CVE-2025-10148.json
- https://github.com/advisories/GHSA-cxvq-c3r3-8gwq
- https://hackerone.com/reports/3330839
- https://nvd.nist.gov/vuln/detail/CVE-2025-10148
