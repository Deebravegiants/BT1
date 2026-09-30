# [C] @react-native-community/cli has arbitrary OS command injection

## Summary
Severity: Critical
Advisory: GHSA-399j-vxmf-hjvr
CVE: CVE-2025-11953
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-399j-vxmf-hjvr
Type: github-advisory

## Affected
- npm: `@react-native-community/cli` — affected >=20.0.0-alpha.0 <20.0.0
- npm: `@react-native-community/cli` — affected >=19.0.0-alpha.0 <19.1.2
- npm: `@react-native-community/cli` — affected >=18.0.0 <18.0.1
- npm: `@react-native-community/cli-server-api` — affected >=20.0.0-alpha.0 <20.0.0
- npm: `@react-native-community/cli-server-api` — affected >=19.0.0-alpha.0 <19.1.2
- npm: `@react-native-community/cli-server-api` — affected >=18.0.0 <18.0.1

## Details
The Metro Development Server, which is opened by the React Native CLI, binds to external interfaces by default. The server exposes an endpoint that is vulnerable to OS command injection. This allows unauthenticated network attackers to send a POST request to the server and run arbitrary executables. On Windows, the attackers can also execute arbitrary shell commands with fully controlled arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11953
- https://github.com/react-native-community/cli/issues/2733#issuecomment-3502424164
- https://github.com/react-native-community/cli/pull/1615
- https://github.com/react-native-community/cli/commit/15089907d1f1301b22c72d7f68846a2ef20df547
- https://github.com/react-native-community/cli/commit/5a792169d9883e0b0fb1ddf1ea46778f21510d18
- https://github.com/react-native-community/cli/commit/9e1fa8cc633e5dcf32244ffa60a871880be56722
- https://github.com/react-native-community/cli/commit/a8293dc29425f56249753507bc24d87b698d46e1
- https://github.com/react-native-community/cli
- https://github.com/react-native-community/cli/releases/tag/v20.0.0
- https://github.com/react-native-community/cli?tab=readme-ov-file#compatibility
- https://jfrog.com/blog/cve-2025-11953-critical-react-native-community-cli-vulnerability
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-11953
- https://www.vulncheck.com/blog/metro4shell_eitw
- https://x.com/SzymonRybczak/status/1986199665000566848
- https://x.com/szymonrybczak/status/1986199665000566848?s=46
- https://x.com/thymikee/status/1986770875954475375
