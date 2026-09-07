# [H] SvelteKit framework has Insufficient CSRF protection for CORS requests

## Summary
Severity: High
Advisory: GHSA-gv7g-x59x-wf8f
CVE: CVE-2023-29008
CWE: CWE-352, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-gv7g-x59x-wf8f
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=0 <1.15.2

## Details
### Summary
The SvelteKit framework offers developers an option to create simple REST APIs. This is done by defining a `+server.js` file, containing endpoint handlers for different HTTP methods.

SvelteKit provides out-of-the-box cross-site request forgery (CSRF) protection to its users. The protection is implemented at `kit/src/runtime/server/respond.js`. While the implementation does a sufficient job of mitigating common CSRF attacks, the protection can be bypassed by simply specifying an upper-cased `Content-Type` header value. The browser will not send uppercase characters on form submission, but this check does not block all expected cross-site requests: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests

### Details
The CSRF protection is implemented using the code shown below.

``` javascript
		const forbidden =
			is_form_content_type(request) &&
			(request.method === 'POST' ||
				request.method === 'PUT' ||
				request.method === 'PATCH' ||
				request.method === 'DELETE') &&
			request.headers.get('origin') !== url.origin;

		if (forbidden) {
			const csrf_error = error(403, `Cross-site ${request.method} form submissions are forbidden`);
			if (request.headers.get('accept') === 'application/json') {
				return json(csrf_error.body, { status: csrf_error.status });
			}
			return text(csrf_error.body.message, { status: csrf_error.status });
		}
```

If the incoming request specifies a POST/PUT/PATCH/DELETE method, the protection will compare the server’s origin with the value of the HTTP Origin header. A mismatch between these values signals that a potential attack has been detected. The final check is performed on the request’s `Content-Type` header whether the value is either `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`. If all the previous checks pass, the request will be rejected with an 403 error response.
However, `is_form_content_type`, which is responsible for checking the value of the `Content-Type` header, is not sufficient to mitigate all possible variations of this type of attack. Since this function is checking `Content-Type` with lower-cased values, and the browser accepts upper-cased `Content-Type` header to be sent, a CSRF attack performed with the `Content-Type` header that contains an upper-cased character (e.g., `text/plaiN`) can circumvent the protection and the request will be processed by the endpoint handler.
<!--
### PoC
1. Set up the SvelteKit with `POST /api/test` endpoint.
2. Replace `REPLACE_DOMAIN` in the following HTML.
``` html
<script>
(async() => {
	await fetch("https://REPLACE_DOMAIN/api/test", {method: "POST", headers:{"Content-Type":"text/plaiN"}, body: "hello=world"});
})();
</script>
```
3. Confirm that a POST request is processed by the server.
-->
### Impact
If abused, this issue will allow malicious requests to be submitted from third-party domains, which can allow execution of operations within the context of the victim's session, and in extreme scenarios can lead to unauthorized access to users’ accounts. This may lead to all POST operations requiring authentication being allowed in the following cases:
1. If the target site sets `SameSite=None` on its auth cookie and the user visits a malicious site in a Chromium-based browser
2. If the target site doesn't set the `SameSite` attribute explicitly and the user visits a malicious site with Firefox/Safari with tracking protections turned off.
3. If the user is visiting a malicious site with a very outdated browser.

### Remediations
It is preferred to update to SvelteKit 1.15.2. It is also recommended to explicitly set `SameSite` to a value other than `None` on authentication cookies especially if the upgrade cannot be done in a timely manner.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-gv7g-x59x-wf8f
- https://nvd.nist.gov/vuln/detail/CVE-2023-29008
- https://github.com/sveltejs/kit/commit/ba436c6685e751d968a960fbda65f24cf7a82e9f
- https://github.com/sveltejs/kit
