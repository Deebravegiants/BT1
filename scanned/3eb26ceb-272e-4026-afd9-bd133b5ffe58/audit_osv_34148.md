# [M] CVE-2025-55183

## Summary
Severity: Medium
Advisory: CVE-2025-55183
Aliases: GHSA-925w-6v3x-g4j4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-55183
Type: osv

## Details
An information leak vulnerability exists in specific configurations of React Server Components versions 19.0.0, 19.0.1 19.1.0, 19.1.1, 19.1.2, 19.2.0 and 19.2.1, including the following packages: react-server-dom-parcel, react-server-dom-turbopack, and react-server-dom-webpack. A specifically crafted HTTP request sent to a vulnerable Server Function may unsafely return the source code of any Server Function. Exploitation requires the existence of a Server Function which explicitly or implicitly exposes a stringified argument.

## References
- https://www.facebook.com/security/advisories/cve-2025-55183
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
