# [H] CVE-2025-55184

## Summary
Severity: High
Advisory: CVE-2025-55184
Aliases: GHSA-2m3v-v2m8-q956
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-55184
Type: osv

## Details
A pre-authentication denial of service vulnerability exists in React Server Components versions 19.0.0, 19.0.1 19.1.0, 19.1.1, 19.1.2, 19.2.0 and 19.2.1, including the following packages: react-server-dom-parcel, react-server-dom-turbopack, and react-server-dom-webpack. The vulnerable code unsafely deserializes payloads from HTTP requests to Server Function endpoints, which can cause an infinite loop that hangs the server process and may prevent future HTTP requests from being served.

## References
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
- https://www.facebook.com/security/advisories/cve-2025-55184
- https://github.com/KingHacker353/CVE-2025-55184
