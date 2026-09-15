# [C] Compromised agents may be able to execute remote code on GoCD Server

## Summary
Severity: Critical
Advisory: CVE-2022-39311
Aliases: GHSA-2hjh-3p3p-8hcm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-39311
Type: osv

## Details
GoCD is a continuous delivery server. GoCD helps you automate and streamline the build-test-release cycle for continuous delivery of your product. GoCD versions prior to 21.1.0 are vulnerable to remote code execution on the server from a malicious or compromised agent. The Spring RemoteInvocation endpoint exposed agent communication and allowed deserialization of arbitrary java objects, as well as subsequent remote code execution. Exploitation requires agent-level authentication, thus an attacker would need to either compromise an existing agent, its network communication or register a new agent to practically exploit this vulnerability. This issue is fixed in GoCD version 21.1.0. There are currently no known workarounds.

## References
- https://www.gocd.org/releases/#21-1-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39311.json
- https://github.com/gocd/gocd/security/advisories/GHSA-2hjh-3p3p-8hcm
- https://nvd.nist.gov/vuln/detail/CVE-2022-39311
- https://github.com/gocd/gocd/commit/7b88b70d6f7f429562d5cab49a80ea856e34cdc8
