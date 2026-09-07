# [H] pgjdbc: Unbounded PBKDF2 iterations in SCRAM authentication allows CPU exhaustion DoS

## Summary
Severity: High
Advisory: GHSA-98qh-xjc8-98pq
CVE: CVE-2026-42198
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-98qh-xjc8-98pq
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=42.2.0 <42.7.11

## Details
## Summary
pgjdbc is vulnerable to a client-side denial of service during SCRAM-SHA-256 authentication.

### Impact
A malicious server can instruct the driver to perform SCRAM authentication with a very large iteration count.
With a large enough value, the client spends an unbounded amount of CPU time inside PBKDF2 before authentication can fail.
A single attempt ties up a CPU core. Repeated or concurrent attempts exhaust client CPU and can wedge connection pools.

In affected versions, `loginTimeout` did not fully mitigate this problem. When `loginTimeout` expired, the caller could stop waiting, but the worker thread performing the connection attempt could continue running and burning CPU inside the SCRAM PBKDF2 computation.

This issue affects availability. It does **not** provide authentication bypass, privilege escalation, or direct password disclosure.

A user is vulnerable when **all** of the following are true:

1. The connection uses **SCRAM-SHA-256** authentication.
2. The client reaches a **malicious, compromised, or attacker-controlled PostgreSQL endpoint**.
3. That endpoint sends a very large SCRAM PBKDF2 iteration count in the `server-first-message`.

In practice, that can happen in these situations:

- the application lets end users or tenants supply their own database connection details (as in many BI, reporting, analytics, ETL, and low-code platforms), so a user can point the shared client host at a server they control
- the application accepts connection strings, hostnames, or JDBC URLs from user input, configuration uploaded by users, or other untrusted sources
- the application is configured to connect to a PostgreSQL server that is itself malicious or later becomes compromised
- the application connects through an untrusted proxy, relay, tunnel, bastion, or connection-pooling service that can act as the PostgreSQL server
- an attacker can redirect the client to a fake PostgreSQL endpoint by manipulating DNS, service discovery, Kubernetes service resolution, `/etc/hosts`, environment variables, or similar indirection
- an active network attacker on the path can impersonate the server because the connection does not strongly verify server identity (for example, `sslmode` lower than `verify-full`, or trusting a CA that signs hosts outside the operator's control)

The issue is **more damaging** when the application uses connection retries, many parallel connection attempts, or `loginTimeout` and assumes the timeout fully stops the work.

### Patches
The patch introduces a new connection property, `scramMaxIterations`, with a default of 100K. The client now rejects SCRAM server messages that advertise more PBKDF2 iterations than the configured cap before starting the PBKDF2 computation begins.

### Workarounds

Until a patched version of pgjdbc is deployed, the following measures reduce exposure:

1. **Only connect to trusted PostgreSQL servers whose identity is verified.**  
   Connect only to trusted PostgreSQL servers, and verify server identity with TLS using sslmode=verify-full and a trusted CA.
   TLS without certificate and hostname verification is not sufficient as an active network attacker can still impersonate the server.

2. **Do not rely on `loginTimeout` as a complete mitigation on unpatched versions.**  
   On affected versions, `loginTimeout` can stop the waiting caller while the worker thread continues spending CPU.

3. **Avoid SCRAM on untrusted or interceptable connection paths.**  
   For those paths, use an authentication method that does not let the server choose a SCRAM PBKDF2 iteration count.

4. **Reduce blast radius operationally.**  
   Limit parallel connection attempts, add retry backoff, isolate connection establishment in a separate worker or process when possible, and apply CPU or container limits where appropriate.

5. **On trusted servers you control, keep SCRAM iteration counts at ordinary values.**  
   This does not defend against an attacker-controlled server, but it avoids unnecessary client cost when talking to legitimate servers.

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-98qh-xjc8-98pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42198
- https://github.com/pgjdbc/pgjdbc
- https://github.com/pgjdbc/pgjdbc/releases/tag/REL42.7.11
