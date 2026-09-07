# [M] Astro Cloudflare adapter has Stored Cross-site Scripting vulnerability in /_image endpoint

## Summary
Severity: Medium
Advisory: GHSA-fvmw-cj7j-j39q
CVE: CVE-2025-65019
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-fvmw-cj7j-j39q
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <5.15.9

## Details
**Summary**  
A Cross-Site Scripting (XSS) vulnerability exists in Astro when using the **@astrojs/cloudflare** adapter with `output: 'server'`. The built-in image optimization endpoint (`/_image`) uses `isRemoteAllowed()` from Astro’s internal helpers, which **unconditionally allows `data:` URLs**. When the endpoint receives a valid `data:` URL pointing to a malicious SVG containing JavaScript, and the Cloudflare-specific implementation performs a **302 redirect back to the original `data:` URL**, the browser directly executes the embedded JavaScript. This completely bypasses any domain allow-listing (`image.domains` / `image.remotePatterns`) and typical Content Security Policy mitigations.

**Affected Versions**  
- `@astrojs/cloudflare` ≤ 12.6.10 (and likely all previous versions)  
- Astro ≥ 4.x when used with `output: 'server'` and the Cloudflare adapter

**Root Cause – Vulnerable Code**  
File: `node_modules/@astrojs/internal-helpers/src/remote.ts`

```ts
export function isRemoteAllowed(src: string, ...): boolean {
  if (!URL.canParse(src)) {
    return false;
  }
  const url = new URL(src);

  // Data URLs are always allowed 
  if (url.protocol === 'data:') {
    return true;
  }

  // Non-http(s) protocols are never allowed
  if (!['http:', 'https:'].includes(url.protocol)) {
    return false;
  }
  // ... further http/https allow-list checks
}
```

In the **Cloudflare adapter**, the `/_image` endpoint contains logic similar to:

```ts
	const href = ctx.url.searchParams.get('href');
	if (!href) {
		// return error 
	}

	if (isRemotePath(href)) {
		if (isRemoteAllowed(href, imageConfig) === false) {
			// return error
		} else {
            //redirect to return the image 
			return Response.redirect(href, 302);
		}
	}
```

Because `data:` URLs are considered “allowed”, a request such as:  
`https://example.com/_image?href=data:image/svg+xml;base64,PHN2Zy... (base64-encoded malicious SVG)`  

triggers a **302 redirect directly to the `data:` URL**, causing the browser to render and execute the malicious JavaScript inside the SVG.

**Proof of Concept (PoC)**  

1. Create a minimal Astro project with Cloudflare adapter (`output: 'server'`).
2. Deploy to Cloudflare Pages or Workers.
3. Request the image endpoint with the following payload:

```
https://yoursite.com/_image?href=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxzY3JpcHQ+YWxlcnQoJ3pvbWFzZWMnKTwvc2NyaXB0Pjwvc3ZnPg==
```

   (Base64 decodes to: `<svg xmlns="http://www.w3.org/2000/svg"><script>alert('zomasec')</script></svg>`)

4. The endpoint returns a **302 redirect** to the `data:` URL → browser executes the `<script>` → `alert()` fires.

**Impact**  
- Reflected/Strored XSS (depending on application usage)  
- Session hijacking (access to cookies, localStorage, etc.)  
- Account takeover when combined with CSRF  
- Data exfiltration to attacker-controlled servers  
- Bypasses `image.domains` / `image.remotePatterns` configuration entirely  

**Safe vs Vulnerable Behavior**  
Other Astro adapters (Node, Vercel, etc.) typically **proxy and rasterize** SVGs, stripping JavaScript. The **Cloudflare adapter** currently **redirects** to remote resources (including `data:` URLs), making it uniquely vulnerable.

**References**  
- Vulnerable function: https://github.com/withastro/astro/blob/main/packages/internal-helpers/src/remote.ts  
- Similar `data:` URL bypass in WordPress: [CVE-2025-2575 ](https://feedly.com/cve/CVE-2025-2575)

## References
- https://github.com/withastro/astro/security/advisories/GHSA-fvmw-cj7j-j39q
- https://nvd.nist.gov/vuln/detail/CVE-2025-65019
- https://github.com/withastro/astro/commit/9e9c528191b6f5e06db9daf6ad26b8f68016e533
- https://github.com/withastro/astro
