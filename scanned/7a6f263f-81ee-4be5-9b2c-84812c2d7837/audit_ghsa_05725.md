# [M] Hono IPv4 address validation bypass in IP Restriction Middleware allows IP spoofing

## Summary
Severity: Medium
Advisory: GHSA-r354-f388-2fhh
CVE: CVE-2026-24398
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-r354-f388-2fhh
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.7

## Details
## Summary

IP Restriction Middleware in Hono is vulnerable to an IP address validation bypass. The `IPV4_REGEX` pattern and `convertIPv4ToBinary` function in `src/utils/ipaddr.ts` do not properly validate that IPv4 octet values are within the valid range of 0-255, allowing attackers to craft malformed IP addresses that bypass IP-based access controls.

## Details

The vulnerability exists in two components:

1. **Permissive regex pattern:** The `IPV4_REGEX (/^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$/)` accepts octet values greater than 255 (e.g., `999`).
2. **Unsafe binary conversion:** The `convertIPv4ToBinary` function does not validate octet ranges before performing bitwise operations. When an octet exceeds 255, it overflows into adjacent octets during the bit-shift calculation.

For example, the IP address `1.2.2.355` is accepted and converts to the same binary value as 1.2.3.99:

* `355` = `256 + 99` = `0x163`
* After bit-shifting: `(1 << 24) + (2 << 16) + (2 << 8) + 355` = `0x01020363` = `1.2.3.99`

## Impact

An attacker can bypass IP-based restrictions by crafting malformed IP addresses:

* **Blocklist bypass:** If `1.2.3.0/24` is blocked, an attacker can use `1.2.2.355` (or similar) to bypass the restriction.
* **Allowlist bypass:** Requests from unauthorized IP ranges may be incorrectly permitted.

This is exploitable when the application relies on client-provided IP addresses (e.g., `X-Forwarded-For header`) for access control decisions.

## Affected Components

* IP Restriction Middleware
* `src/utils/ipaddr.ts`: `IPV4_REGEX`, `convertIPv4ToBinary`, `distinctRemoteAddr`

## References
- https://github.com/honojs/hono/security/advisories/GHSA-r354-f388-2fhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24398
- https://github.com/honojs/hono/commit/edbf6eea8e6c26a3937518d4ed91d8666edeec37
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.11.7
