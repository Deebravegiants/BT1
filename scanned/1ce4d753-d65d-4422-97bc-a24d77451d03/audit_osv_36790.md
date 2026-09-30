# [M] Wazuh Vulnerable to Denial of Service via Synchronous I/O Blocking in Asynchronous Authentication Middleware

## Summary
Severity: Medium
Advisory: CVE-2026-25771
Aliases: GHSA-33w3-p5hm-jw7g
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-25771
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. Starting in version 4.3.0 and prior to version 4.14.3, a Denial of Service (DoS) vulnerability exists in the Wazuh API authentication middleware (`middlewares.py`). The application uses an asynchronous event loop (Starlette/Asyncio) to call a synchronous function (`generate_keypair`) that performs blocking disk I/O on every request containing a Bearer token. An unauthenticated remote attacker can exploit this by flooding the API with requests containing invalid Bearer tokens. This forces the single-threaded event loop to pause for file read operations repeatedly, starving the application of CPU resources and potentially preventing it from accepting or processing legitimate connections. Version 4.14.3 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25771.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-33w3-p5hm-jw7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-25771
