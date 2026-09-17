# [M] Hono has incorrect IP matching in ipRestriction() for IPv4-mapped IPv6 addresses

## Summary
Severity: Medium
Advisory: GHSA-xpcf-pg52-r92g
CVE: CVE-2026-39409
CWE: CWE-180
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-xpcf-pg52-r92g
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.12

## Details
## Summary

`ipRestriction()` does not canonicalize IPv4-mapped IPv6 client addresses (e.g. `::ffff:127.0.0.1`) before applying IPv4 allow or deny rules. In environments such as Node.js dual-stack, this can cause IPv4 rules to fail to match, leading to unintended authorization behavior.

## Details

The middleware classifies client addresses based on their textual form. Addresses containing "`:`" are treated as IPv6, including IPv4-mapped IPv6 addresses such as `::ffff:127.0.0.1`. These addresses are not normalized to IPv4 before matching.

As a result:

* IPv4 static rules (e.g. `127.0.0.1`) do not match because the raw string differs
* IPv4 CIDR rules (e.g. `127.0.0.0/8`, `10.0.0.0/8`) are skipped because the address is treated as IPv6

For example, with:

`denyList: ['127.0.0.1']`

a request from `127.0.0.1` may be represented as `::ffff:127.0.0.1` and bypass the deny rule.

This behavior commonly occurs in Node.js environments where IPv4 clients are exposed as IPv4-mapped IPv6 addresses.

## Impact

Applications that rely on IPv4-based `ipRestriction()` rules may incorrectly allow or deny requests.

In affected deployments, a denied IPv4 client may bypass access restrictions. Conversely, legitimate clients may be rejected when using IPv4 allow lists.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-xpcf-pg52-r92g
- https://nvd.nist.gov/vuln/detail/CVE-2026-39409
- https://github.com/honojs/hono/commit/48fa2233bc092f650119f42df043050737cabf39
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.12
