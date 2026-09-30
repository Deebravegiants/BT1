# [M] RansomLook Login Endpoint Allows Timing-Based Username Enumeration and Unthrottled Authentication Attempts

## Summary
Severity: Medium
Advisory: CVE-2026-78551
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78551
Type: osv

## Details
RansomLook contains multiple weaknesses in its authentication endpoint that allow an unauthenticated remote attacker to enumerate valid usernames, perform unrestricted password-guessing attacks, and potentially exhaust application worker resources.

For local authentication, the login implementation previously checked whether a submitted username existed before invoking the password hash verification function. Requests containing a nonexistent username therefore returned significantly faster than requests for valid accounts, for which the computationally expensive password verification routine was executed. A remote attacker could measure these response-time differences to determine which usernames correspond to valid RansomLook accounts.

In addition, the /login endpoint did not restrict the number or frequency of failed authentication attempts. An attacker could consequently perform password brute-force, dictionary, password-spraying, or credential-stuffing attacks against known accounts without server-side throttling. For valid usernames, each authentication attempt also invokes the password key-derivation function, which consumes a significant amount of CPU time. A sufficiently high rate of login attempts could therefore occupy the application's synchronous Gunicorn workers and cause a denial of service affecting the entire application.

The issue has been addressed by always performing password verification using a randomly generated dummy password hash when the supplied username does not exist, eliminating the username-dependent timing discrepancy. Failed authentication attempts are additionally rate-limited per client IP address using Valkey/Redis, with five failed attempts within five minutes resulting in a one-hour block. The reverse-proxy configuration was also updated so that the application derives the client address from a trusted X-Forwarded-For value that cannot be overridden by a client-supplied header.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78551.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78551
- https://github.com/RansomLook/RansomLook/commit/8602740347b0e928ad9fbaf5bc6ff242337dec6b
