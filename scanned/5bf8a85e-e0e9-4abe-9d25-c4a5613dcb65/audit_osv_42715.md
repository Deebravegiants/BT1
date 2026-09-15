# [M] boringproxy 0.10.0 SSH authorized_keys Injection via Tunnel Creation

## Summary
Severity: Medium
Advisory: CVE-2026-70615
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70615
Type: osv

## Details
boringproxy through 0.10.0 contains a newline injection vulnerability that allows authenticated low-privileged users with tunnel-creation permission to inject arbitrary lines into the server account's SSH authorized_keys file by supplying a percent-encoded newline character in the domain parameter of the tunnel creation endpoint. Attackers can insert an unrestricted public key entry into authorized_keys to gain persistent shell access, and subsequently read cleartext credentials from the database file including all user tokens, tunnel private keys, and TLS certificates.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70615.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70615
- https://www.vulncheck.com/advisories/boringproxy-ssh-authorized-keys-injection-via-tunnel-creation
- https://github.com/boringproxy/boringproxy
- https://github.com/theopaid/Remote-Code-Execution-And-Privilege-Escalation-Through-SSH-Authorized-Keys-Injection-boringproxy-/blob/master/README.md
