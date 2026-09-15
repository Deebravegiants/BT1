# [M] Better Call routing bug can lead to Cache Deception

## Summary
Severity: Medium
Advisory: GHSA-hq75-xg7r-rx6c
CWE: CWE-525
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-07-11
Source: https://github.com/advisories/GHSA-hq75-xg7r-rx6c
Type: github-advisory

## Affected
- npm: `better-call` — affected >=0 <1.0.12

## Details
### Summary

Using a CDN that caches (`/**/*.png`, `/**/*.json`, `/**/*.css`, etc...) requests, a cache deception can emerge. This could lead to unauthorized access to user sessions and personal data when cached responses are served to other users.

### Details

The vulnerability occurs in the request processing logic where path sanitization is insufficient. The library splits the path using `config.basePath` but doesn't properly validate the remaining path components. This allows specially crafted requests that appear to be static assets (like `/api/auth/get-session/api/auth/image.png` assuming `config.basePath`=`/api/auth`) to bypass typical CDN cache exclusion rules while actually returning sensitive data.

The problematic code [here](https://github.com/Bekacru/better-call/blob/8b6f13e24fad7f4666a582601517bb3232d4f4af/src/router.ts#L124):
```js
	const processRequest = async (request: Request) => {
		const url = new URL(request.url);
		const path = config?.basePath ? url.pathname.split(config.basePath)[1] : url.pathname;
```

Since this library is largely coupled with `better-auth`, it becomes more clear why this can be dangerous with an example request:

<img width="800" alt="image" src="https://github.com/user-attachments/assets/2ab7c4dd-0700-4f59-863f-79f2b5edbb37" />

### Impact

This is a cache deception vulnerability affecting `better-call` users with CDN caching enabled. which can expose sensitive data.

## References
- https://github.com/Bekacru/better-call/security/advisories/GHSA-hq75-xg7r-rx6c
- https://github.com/Bekacru/better-call/commit/7c7d31b
- https://github.com/Bekacru/better-call
