# [M] Faktory: Unrecovered panic in command handlers allows full-server denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-63403
Aliases: GHSA-gc57-f6pg-m9h6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-63403
Type: osv

## Details
Faktory is a language-agnostic background job server. In versions prior to 1.10.0, the server is vulnerable to an unauthenticated denial of service in which a single malformed command crashes the entire process. Its wire protocol is line-based, and several command handlers slice or index the received line at a fixed offset, such as cmd[5:] for PUSH or qs[0] for QUEUE, without checking that a payload is present. Sending a bare verb with no payload, for example PUSH, ACK, FAIL, BEAT, PUSHB, or QUEUE, triggers a Go slice or index out-of-range panic. Because the codebase has no recover() anywhere in the command-dispatch path, an unrecovered panic in a handler goroutine terminates the whole Go process rather than just that connection, instantly disconnecting every other client, worker, and in-flight job. The attack requires only a connection to the command port and completion of the trivial handshake, with no credentials when no password is configured, and can be repeated to keep the service down indefinitely. This issue is fixed in version 1.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63403.json
- https://github.com/contribsys/faktory/security/advisories/GHSA-gc57-f6pg-m9h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-63403
- http://github.com/contribsys/faktory/commit/c2f17e390fc7d38b6ece82b8da23f5ca15646212
