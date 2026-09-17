# [H] Coturn has unsafe nonce and relay port randomization due to weak random number generation.

## Summary
Severity: High
Advisory: CVE-2025-69217
Aliases: GHSA-fvj6-9jhg-9j84
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2025-69217
Type: osv

## Details
coturn is a free open source implementation of TURN and STUN Server. Versions 4.6.2r5 through 4.7.0-r4 have a bad random number generator for nonces and port randomization after refactoring. Additionally, random numbers aren't generated with openssl's RAND_bytes but libc's random() (if it's not running on Windows). When fetching about 50 sequential nonces (i.e., through sending 50 unauthenticated allocations requests) it is possible to completely reconstruct the current state of the random number generator, thereby predicting the next nonce. This allows authentication while spoofing IPs. An attacker can send authenticated messages without ever receiving the responses, including the nonce (requires knowledge of the credentials, which is e.g., often the case in IoT settings). Since the port randomization is deterministic given the pseudorandom seed, an attacker can exactly reconstruct the ports and, hence predict the randomization of the ports. If an attacker allocates a relay port, they know the current port, and they are able to predict the next relay port (at least if it is not used before). Commit 11fc465f4bba70bb0ad8aae17d6c4a63a29917d9 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69217.json
- https://github.com/coturn/coturn/security/advisories/GHSA-fvj6-9jhg-9j84
- https://nvd.nist.gov/vuln/detail/CVE-2025-69217
- https://github.com/coturn/coturn/commit/11fc465f4bba70bb0ad8aae17d6c4a63a29917d9
- https://github.com/coturn/coturn/commit/88ced471385869d7e7fbbc4766e78ef521b36af6
