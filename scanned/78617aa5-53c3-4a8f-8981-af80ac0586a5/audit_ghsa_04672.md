# [M] Hono: IP Restriction bypasses static deny rules for non-canonical IPv6 

## Summary
Severity: Medium
Advisory: GHSA-xrhx-7g5j-rcj5
CVE: CVE-2026-47674
CWE: CWE-1289, CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-xrhx-7g5j-rcj5
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.21

## Details
### Summary

The `ip-restriction` middleware (`hono/ip-restriction`) compares incoming IP addresses against configured deny and allow rules using string equality after partial normalization. Non-canonical IPv6 representations of an address already listed in a static rule — such as compressed forms, explicit-zero forms, or hex-notation IPv4-mapped addresses — do not match the normalized rule entry, causing the rule to be silently skipped.

### Details

When the rule matcher is built, each configured IP rule is normalized to a canonical string form. Incoming IP addresses received at request time are then compared against those canonical strings without applying the same normalization. Because IPv6 permits multiple syntactically different representations of the same numeric address, a non-canonical form of a denied address fails the string lookup and proceeds to the CIDR check, which also finds no match for rules registered as static (no prefix length). The request is then allowed.

Affected non-canonical forms include:

- Compressed versus expanded notation (`2001:db8::1` vs `2001:db8:0:0:0:0:0:1`)
- Hex-notation IPv4-mapped addresses (`::ffff:7f00:1` vs `::ffff:127.0.0.1`)
- Zone identifier suffixes (e.g., `fe80::1%eth0`)

Additionally, invalid IP address strings provided as the remote address are not rejected and may result in unexpected allow or deny behavior.

This issue arises when applications use `ipRestriction()` with static (non-CIDR) rules and the IP address source can supply addresses in non-canonical IPv6 form.

### Impact

A request from an IP address covered by a static deny rule may bypass the restriction if the address is presented in a non-canonical IPv6 form.

This may lead to:

- Unauthorized access to endpoints intended to be restricted to specific IP addresses
- Bypass of IP-based access controls in environments where the runtime or an upstream proxy provides source addresses in a form that differs from the canonical form used in the rule configuration

This issue affects applications using `hono/ip-restriction` with static deny rules for IPv4 or IPv6 addresses, particularly when the source address is derived from proxy headers or custom `getIP` implementations that may return non-canonical forms.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-xrhx-7g5j-rcj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-47674
- https://github.com/honojs/hono/commit/c831020fb1fa2e929d222f6c84e1abfe013e512b
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.21
