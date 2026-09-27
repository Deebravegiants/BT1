# [H] Next.js Server-Side Request Forgery in Server Actions

## Summary
Severity: High
Advisory: GHSA-fr5h-rqp8-mj6g
CVE: CVE-2024-34351
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-09
Source: https://github.com/advisories/GHSA-fr5h-rqp8-mj6g
Type: github-advisory

## Affected
- npm: `next` — affected >=13.4.0 <14.1.1

## Details
### Impact
A Server-Side Request Forgery (SSRF) vulnerability was identified in Next.js Server Actions by security researchers at Assetnote. If the `Host` header is modified, and the below conditions are also met, an attacker may be able to make requests that appear to be originating from the Next.js application server itself.

#### Prerequisites
* Next.js (`<14.1.1`) is running in a self-hosted* manner.
* The Next.js application makes use of Server Actions.
* The Server Action performs a redirect to a relative path which starts with a `/`.

\* Many hosting providers (including Vercel) route requests based on the Host header, so we do not believe that this vulnerability affects any Next.js applications where routing is done in this manner.

### Patches
This vulnerability was patched in [#62561](https://github.com/vercel/next.js/pull/62561) and fixed in Next.js `14.1.1`.
 
### Workarounds
There are no official workarounds for this vulnerability. We recommend upgrading to Next.js `14.1.1`.

### Credit
Vercel and the Next.js team thank Assetnote for responsibly disclosing this issue to us, and for working with us to verify the fix. Thanks to:

Adam Kues - Assetnote
Shubham Shah - Assetnote

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-fr5h-rqp8-mj6g
- https://nvd.nist.gov/vuln/detail/CVE-2024-34351
- https://github.com/vercel/next.js/pull/62561
- https://github.com/vercel/next.js/commit/8f7a6ca7d21a97bc9f7a1bbe10427b5ad74b9085
- https://github.com/vercel/next.js
