# [H] @fastify/secure-session: Reuse of destroyed secure session cookie

## Summary
Severity: High
Advisory: GHSA-9wwp-q7wq-jx35
CVE: CVE-2024-31999
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-9wwp-q7wq-jx35
Type: github-advisory

## Affected
- npm: `@fastify/secure-session` — affected >=0 <7.3.0

## Details
### Impact

At the end of the request handling, it will encrypt all data in the session with a secret key and attach the ciphertext as a cookie value with the defined cookie name. After that, the session on the server side is destroyed. When an encrypted cookie with matching session name is provided with subsequent requests, it will decrypt the ciphertext to get the data. The plugin then creates a new session with the data in the ciphertext. Thus theoretically the web instance is still accessing the data from a server-side session, but technically that session is generated solely from a user provided cookie (which is assumed to be non-craftable because it is encrypted with a secret key not known to the user).

The issue exists in the session removal process. In the delete function of the code, when the session is deleted, it is marked for deletion. However, if an attacker could gain access to the cookie, they could keep using it forever.

### Patches

Fixed in 56d66642ecc633cff0606927601e81cdac361370.
Update to v7.3.0.

### Workarounds

Include a "last update" field in the session, and treat "old sessions" as expired. 
Make sure to configure your cookie as "http only".

### References

* https://hackerone.com/reports/2374253

## References
- https://github.com/fastify/fastify-secure-session/security/advisories/GHSA-9wwp-q7wq-jx35
- https://nvd.nist.gov/vuln/detail/CVE-2024-31999
- https://github.com/fastify/fastify-secure-session/commit/56d66642ecc633cff0606927601e81cdac361370
- https://github.com/fastify/fastify-secure-session
