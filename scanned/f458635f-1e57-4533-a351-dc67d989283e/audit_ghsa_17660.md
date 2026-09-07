# [H] OpenNext for Cloudflare (opennextjs-cloudflare) has a SSRF vulnerability via /_next/image endpoint

## Summary
Severity: High
Advisory: GHSA-rvpw-p7vw-wj3m
CVE: CVE-2025-6087
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-rvpw-p7vw-wj3m
Type: github-advisory

## Affected
- npm: `@opennextjs/cloudflare` — affected >=0 <1.3.0

## Details
A Server-Side Request Forgery (SSRF) vulnerability was identified in the @opennextjs/cloudflare package. 

The vulnerability stems from an unimplemented feature in the Cloudflare adapter for Open Next, which allowed unauthenticated users to proxy arbitrary remote content via the `/_next/image` endpoint. 

This issue allowed attackers to load remote resources from arbitrary hosts under the victim site’s domain for any site deployed using the Cloudflare adapter for Open Next.  For example: `https://victim-site.com/_next/image?url=https://attacker.com`. In this example, attacker-controlled content from attacker.com is served through the victim site’s domain (`victim-site.com`), violating the same-origin policy and potentially misleading users or other services.

### Impact

- SSRF via unrestricted remote URL loading 
- Arbitrary remote content loading 
- Potential internal service exposure or phishing risks through domain abuse 


### Mitigation

The following mitigations have been put in place: 

**Server side updates** to Cloudflare’s platform to restrict the content loaded via the `/_next/image` endpoint to images. The update automatically mitigates the issue for all existing and any future sites deployed to Cloudflare using the affected version of the Cloudflare adapter for Open Next 

**Root cause fix**: Pull request https://github.com/opennextjs/opennextjs-cloudflare/pull/727  to the Cloudflare adapter for Open Next. The patched version of the adapter is found here  [@opennextjs/cloudflare@1.3.0](https://www.npmjs.com/package/@opennextjs/cloudflare/v/1.3.0)

**Package dependency update**: Pull request https://github.com/cloudflare/workers-sdk/pull/9608  to create-cloudflare (c3) to use the fixed version of the Cloudflare adapter for Open Next. The patched version of create-cloudflare is found at [create-cloudflare@2.49.3](https://www.npmjs.com/package/create-cloudflare/v/2.49.3).

 In addition to the automatic mitigation deployed on Cloudflare’s platform, we encourage affected users to upgrade to @opennext/cloudflare v1.3.0 and use the [remotePatterns](https://nextjs.org/docs/pages/api-reference/components/image#remotepatterns) filter in Next config if they need to allow-list external urls with images assets.

### Credits

Disclosed responsibly by security researcher Edward Coristine. Thank you for the report.

### References

https://www.cve.org/cverecord?id=CVE-2025-6087

## References
- https://github.com/opennextjs/opennextjs-cloudflare/security/advisories/GHSA-rvpw-p7vw-wj3m
- https://nvd.nist.gov/vuln/detail/CVE-2025-6087
- https://github.com/cloudflare/workers-sdk/pull/9608
- https://github.com/opennextjs/opennextjs-cloudflare/pull/727
- https://github.com/opennextjs/opennextjs-cloudflare/commit/36119c0f490c95b3d4f6e826d745b728c80625ab
- https://github.com/opennextjs/opennextjs-cloudflare
