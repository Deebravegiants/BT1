# [C] HTTP Handling Vulnerability in the Bare server

## Summary
Severity: Critical
Advisory: GHSA-86fc-f9gr-v533
CVE: CVE-2024-27922
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-05
Source: https://github.com/advisories/GHSA-86fc-f9gr-v533
Type: github-advisory

## Affected
- npm: `@tomphttp/bare-server-node` — affected >=0 <2.0.2

## Details
### Impact
This vulnerability relates to insecure handling of HTTP requests by the @tomphttp/bare-server-node package. This flaw potentially exposes the users of the package to manipulation of their web traffic. The impact may vary depending on the specific usage of the package but it can potentially affect any system where this package is in use.

### Patches
Yes, the problem has been patched. We advise all users to upgrade to version @tomphttp/bare-server-node@2.0.2 as soon as possible.

### Workarounds
Given the nature of the vulnerability, the most effective solution is to upgrade to the patched version of the package. Specific workaround strategies will be disclosed later due to security considerations.

### References
Further information about this vulnerability will be provided at a later date to provide users with an opportunity to upgrade to a patched version and to prevent potential exploitation of the vulnerability. Users are advised to follow the repository announcements and updates.

## References
- https://github.com/tomphttp/bare-server-node/security/advisories/GHSA-86fc-f9gr-v533
- https://nvd.nist.gov/vuln/detail/CVE-2024-27922
- https://github.com/tomphttp/bare-server-node
