# [H] CVE-2025-67779

## Summary
Severity: High
Advisory: CVE-2025-67779
Aliases: GHSA-7gmr-mq3h-m5h9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-12
Source: https://osv.dev/vulnerability/CVE-2025-67779
Type: osv

## Details
It was found that the fix addressing CVE-2025-55184 in React Server Components was incomplete and does not prevent a denial of service attack in a specific case. React Server Components versions 19.0.2, 19.1.3 and 19.2.2 are affected, allowing unsafe deserialization of payloads from HTTP requests to Server Function endpoints. This can cause an infinite loop that hangs the server process and may prevent future HTTP requests from being served.

## References
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
- https://www.facebook.com/security/advisories/cve-2025-67779
