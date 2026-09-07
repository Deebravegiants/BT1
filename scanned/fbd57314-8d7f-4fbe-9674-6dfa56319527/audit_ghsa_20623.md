# [H] Improper token validation leading to code execution in Teleport

## Summary
Severity: High
Advisory: GHSA-6xf3-5hp7-xqqg
CVE: CVE-2022-36633
CWE: CWE-20, CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-6xf3-5hp7-xqqg
Type: github-advisory

## Affected
- Go: `github.com/gravitational/teleport` — affected >=0 <8.3.17
- Go: `github.com/gravitational/teleport` — affected >=9.0.0 <9.3.13
- Go: `github.com/gravitational/teleport` — affected >=10.0.0 <10.1.2

## Details
Teleport 9.3.6 is vulnerable to Command injection leading to Remote Code Execution. An attacker can craft a malicious ssh agent installation link by URL encoding a bash escape with carriage return line feed. This url encoded payload can be used in place of a token and sent to a user in a social engineering attack. This is fully unauthenticated attack utilizing the trusted teleport server to deliver the payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36633
- https://github.com/gravitational/teleport/pull/14726
- https://github.com/gravitational/teleport/pull/14726/commits/46c23b9b64b944d1e82d2c8a79083f291ffdd3b6
- https://github.com/gravitational/teleport
- https://github.com/gravitational/teleport/releases/tag/v10.1.2
- https://github.com/gravitational/teleport/releases/tag/v8.3.17
- https://github.com/gravitational/teleport/releases/tag/v9.3.13
- https://packetstormsecurity.com/files/168137/Teleport-9.3.6-Command-Injection.html
- http://packetstormsecurity.com/files/168477/Teleport-10.1.1-Remote-Code-Execution.html
