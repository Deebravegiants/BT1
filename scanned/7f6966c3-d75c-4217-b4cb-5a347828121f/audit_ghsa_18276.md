# [M] Coder AgentAPI exposed user chat history via a DNS rebinding attack

## Summary
Severity: Medium
Advisory: GHSA-w64r-2g3w-w8w4
CVE: CVE-2025-59956
CWE: CWE-290, CWE-350
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-w64r-2g3w-w8w4
Type: github-advisory

## Affected
- Go: `github.com/coder/agentapi` — affected >=0 <0.4.0

## Details
### Summary
AgentAPI prior to version [0.4.0](https://github.com/coder/agentapi/releases/tag/v0.4.0) was susceptible to a client-side DNS rebinding attack when hosted over plain HTTP on localhost.

### Impact
An attacker could have gained access to the `/messages` endpoint served by the Agent API. This allowed for the unauthorized exfiltration of sensitive user data, specifically local message history, which could've included secret keys, file system contents, and intellectual property the user was working on locally.

### Remediation
We've [implemented](https://github.com/coder/agentapi/pull/49) an `Origin` and `Host` header validating middleware and set a secure by default configuration.

Please upgrade to version [0.4.0](https://github.com/coder/agentapi/releases/tag/v0.4.0) or later.

### Credits
We'd like to thank [Evan Harris](https://github.com/eharris128) from [mcpsec.dev](https://mcpsec.dev/) for reporting this issue and following the coordinated disclosure [policy](https://coder.com/security/policy).

## References
- https://github.com/coder/agentapi/security/advisories/GHSA-w64r-2g3w-w8w4
- https://nvd.nist.gov/vuln/detail/CVE-2025-59956
- https://github.com/coder/agentapi/pull/49
- https://github.com/coder/agentapi/commit/5c425c62447b8a9eac19e9fc5a2eae7f0803f149
- https://github.blog/security/application-security/localhost-dangers-cors-and-dns-rebinding
- https://github.com/coder/agentapi
- https://github.com/coder/agentapi/releases/tag/v0.4.0
- https://mcpsec.dev/advisories/2025-09-19-coder-chat-exfiltration
- https://pkg.go.dev/vuln/GO-2025-3991
