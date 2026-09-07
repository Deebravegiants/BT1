# [M] CrateDB has a Client initialized Session-Renegotiation DoS

## Summary
Severity: Medium
Advisory: GHSA-x268-qpg6-w9g2
CVE: CVE-2024-37309
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-x268-qpg6-w9g2
Type: github-advisory

## Affected
- Maven: `io.crate:crate` — affected >=0 <5.7.2

## Details
**Summary**  
Client-Initiated TLS Renegotiation Denial of Service (DoS) Vulnerability at Port 4200

**Details**  
A high-risk vulnerability has been identified where the TLS endpoint (port 4200) permits client-initiated renegotiation. In this scenario, an attacker can exploit this feature to repeatedly request renegotiation of security parameters during an ongoing TLS session. This flaw could lead to excessive consumption of CPU resources, resulting in potential server overload and service disruption. The vulnerability was confirmed using an openssl client where the command 'R' initiates renegotiation, followed by the server confirming with 'RENEGOTIATING'.

**PoC**  
1. Connect to the TLS server on port 4200 using an openssl client.
2. Initiate a TLS session.
3. Send the renegotiation command ('R') multiple times.
4. Observe the server response to confirm renegotiation.

**Impact**  
This vulnerability allows an attacker to perform a denial of service attack by exhausting server CPU resources through repeated TLS renegotiations. This impacts the availability of services running on the affected server, posing a significant risk to operational stability and security.


TLS 1.3 explicitly forbids renegotiation, since it closes a window of opportunity for an attack.

## References
- https://github.com/crate/crate/security/advisories/GHSA-x268-qpg6-w9g2
- https://nvd.nist.gov/vuln/detail/CVE-2024-37309
- https://github.com/crate/crate/commit/1dde03bdf031a20886065195527e368e4a3218b3
- https://cratedb.com/docs/crate/reference/en/latest/appendices/release-notes/5.7.2.html
- https://github.com/crate/crate
