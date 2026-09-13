# [H] @angular/service-worker: Sensitive Header Leakage on Cross-Origin Redirects in Angular Service Worker

## Summary
Severity: High
Advisory: GHSA-qxh6-94w6-9r5p
CVE: CVE-2026-54264
CWE: CWE-200, CWE-359
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-qxh6-94w6-9r5p
Type: github-advisory

## Affected
- npm: `@angular/service-worker` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/service-worker` — affected >=21.0.0-next.0 <21.2.17
- npm: `@angular/service-worker` — affected >=20.0.0-next.0 <20.3.25
- npm: `@angular/service-worker` — affected >=0

## Details
An information disclosure vulnerability exists in the `@angular/service-worker` package of the Angular framework. When the Service Worker fetches assets, it preserves metadata (such as headers) from the original request. However, on cross-origin redirects, the Service Worker fails to strip sensitive headers, violating the Fetch redirect algorithm. 

This allows a remote attacker to obtain sensitive credentials (e.g., `Authorization` tokens, `Proxy-Authorization` credentials, or session cookies) by triggering a cross-origin redirect to an untrusted external origin.

### Impact
If an application configured with the Angular Service Worker fetches assets with credential headers (such as `Authorization` header), and one of those requests is redirected to a different origin, the Service Worker will forward those headers to the new origin. This exposes critical credentials and session identifiers to unauthorized third-party servers.

### Attack Preconditions
For this vulnerability to be exploitable:
1. **Vulnerable Configuration:** The application must utilize the `@angular/service-worker` package to fetch assets.
2. **Credentialed Requests:** The application must attach sensitive request headers (like `Authorization`, `Proxy-Authorization`, or rely on cookies) to asset-group requests.
3. **Redirect Flow:** These requests must encounter a cross-origin redirect to an attacker-controlled or untrusted domain.

### Patched Versions
* 22.0.1  
* 21.2.17  
* 20.3.25

### Credits
This vulnerability was discovered and reported by [CodeMender from Google DeepMind](https://deepmind.google/blog/introducing-codemender-an-ai-agent-for-code-security/).

## References
- https://github.com/angular/angular/security/advisories/GHSA-qxh6-94w6-9r5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-54264
- https://github.com/angular/angular/pull/69029
- https://github.com/angular/angular/commit/47d68dcb26266316647133ab6385e77fc3e5ae08
- https://github.com/angular/angular
