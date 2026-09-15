# [M] predictable WebSocket mask

## Summary
Severity: Medium
Advisory: CVE-2025-10148
Aliases: CURL-CVE-2025-10148
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/CVE-2025-10148
Type: osv

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
- https://hackerone.com/reports/3330839
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10148.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10148
