# [H] CVE-2026-23869

## Summary
Severity: High
Advisory: CVE-2026-23869
Aliases: GHSA-479c-33wc-g2pg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-23869
Type: osv

## Details
A denial of service vulnerability exists in React Server Components, affecting the following packages: react-server-dom-parcel, react-server-dom-turbopack and react-server-dom-webpack (versions 19.0.0 through 19.0.4, 19.1.0 through 19.1.5, and 19.2.0 through 19.2.4). The vulnerability is triggered by sending specially crafted HTTP requests to Server Function endpoints.The payload of the HTTP request causes excessive CPU usage for up to a minute ending in a thrown error that is catchable.

## References
- https://access.redhat.com/security/cve/CVE-2026-23869
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23869.json
- https://github.com/facebook/react/security/advisories/GHSA-479c-33wc-g2pg
- https://bugzilla.redhat.com/show_bug.cgi?id=2456663
