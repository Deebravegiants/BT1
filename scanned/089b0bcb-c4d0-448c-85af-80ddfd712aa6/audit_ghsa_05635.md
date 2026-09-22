# [H] flagd: Multiple Go Runtime CVEs Impact Security and Availability

## Summary
Severity: High
Advisory: GHSA-4c5f-9mj4-m247
CWE: CWE-20, CWE-362, CWE-400, CWE-407, CWE-444, CWE-770
Ecosystem: Go
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-4c5f-9mj4-m247
Type: github-advisory

## Affected
- Go: `github.com/open-feature/flagd/core` — affected >=0 <0.13.1
- Go: `github.com/open-feature/flagd/flagd-proxy` — affected >=0 <0.8.2
- Go: `github.com/open-feature/flagd/flagd` — affected >=0 <0.13.1

## Details
### Summary
In 2025, several vulnerabilities in the Go Standard Library were disclosed, impacting Go-based applications like flagd (the evaluation engine for OpenFeature). These CVEs primarily focus on Denial of Service (DoS) through resource exhaustion and Race Conditions in database handling. 

| CVE ID | Impacted Package | Severity | Description & Impact on flagd |
| -- | -- | -- | -- |
| CVE-2025-47907 | database/sql | 7.0 (High) | Race Condition:  Canceling a query during a Scan call can return data from the wrong query. Critical if flagd uses SQL-based sync providers (e.g., Postgres), potentially leading to incorrect flag configurations. |
| CVE-2025-61725 | net/mail | 7.5 (High) | DoS: Inefficient complexity in ParseAddress.  Attackers can provide crafted email strings with large domain literals to exhaust CPU if flagd parses email-formatted metadata. |
| CVE-2025-61723 | encoding/pem | 7.5 (High) | DoS: Quadratic complexity when parsing invalid PEM inputs. Relevant if flagd loads TLS certificates or keys via PEM files from untrusted sources. |
| CVE-2025-61729 | crypto/x509 | 7.5 (High) | Resource Exhaustion: HostnameError.Error() lacks string concatenation limits. A malicious TLS certificate with thousands of hostnames could crash flagd during connection handshakes. |
| CVE-2025-58188 | net/http | Medium | Request Smuggling: Improper header handling in HTTP/1.1. Could allow attackers to bypass security filters positioned in front of flagd sync or evaluation APIs. |
| CVE-2025-58187 | archive/zip | Medium | DoS:  Improper validation of malformed ZIP archives.  Impacts flagd if configured to fetch and unpack zipped configuration bundles from remote providers. |

## References
- https://github.com/open-feature/flagd/security/advisories/GHSA-4c5f-9mj4-m247
- https://github.com/open-feature/flagd/pull/1840
- https://github.com/open-feature/flagd
- https://github.com/open-feature/flagd/releases/tag/core%2Fv0.13.1
