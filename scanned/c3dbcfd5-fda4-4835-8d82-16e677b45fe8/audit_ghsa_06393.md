# [H] fast-uri vulnerable to server-side request forgery via malformed IPv6 normalization

## Summary
Severity: High
Advisory: GHSA-f65p-4m7j-42xc
CVE: CVE-2026-75975
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-f65p-4m7j-42xc
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=2.3.1 <2.4.5
- npm: `fast-uri` — affected >=3.0.0 <3.1.6
- npm: `fast-uri` — affected >=4.0.0 <4.1.3

## Details
### Impact

`fast-uri` does not validate the complete RFC 3986 grammar for bracketed IPv6 literals, so a malformed literal with invalid trailing text is silently truncated to a different valid IPv6 address with no error reported. For example, `normalize('http://[::not-valid]/private')` returns `http://[::]/private`, and `[fc00::not-hex]` and `[fe80::not-hex]` collapse to `[fc00::]` and `[fe80::]`. An application that normalizes an untrusted URL before an outbound request, redirect, or host-policy check can be routed to a local or private address such as loopback (`::1`), unique-local, or link-local. Because `parse().error` is unset for these inputs, checking it does not protect the consumer.

### Patches

Upgrade to `fast-uri` 2.4.5, 3.1.6, or 4.1.3. Malformed IPv6 literals are now rejected with a host error instead of being normalized to a valid address.

### Workarounds

Reject untrusted URLs whose host is a bracketed IPv6 literal before passing them to `fast-uri`, or route outbound requests against an explicit allowlist of addresses rather than trusting the normalized host.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-f65p-4m7j-42xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-75975
- https://github.com/fastify/fast-uri/commit/3728465caacef4b16bc84b7d14760f1c8fe41595
- https://github.com/fastify/fast-uri/commit/607bfbe953f28a14c2e06ae64aff38c81ca2937f
- https://github.com/fastify/fast-uri/commit/9161eded1ff55fad9d9714c6ad6c0f0283547799
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fast-uri
- https://github.com/fastify/fast-uri/releases/tag/v2.4.5
- https://github.com/fastify/fast-uri/releases/tag/v3.1.6
- https://github.com/fastify/fast-uri/releases/tag/v4.1.3
