# [H] SvelteKit vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-5p75-vc5g-8rv2
CVE: CVE-2023-29003
CWE: CWE-184, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-5p75-vc5g-8rv2
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=0 <1.15.1

## Details
### Summary
The SvelteKit framework offers developers an option to create simple REST APIs. This is done by defining a `+server.js` file, containing endpoint handlers for different HTTP methods.

SvelteKit provides out-of-the-box cross-site request forgery (CSRF) protection to it’s users. The protection is implemented at `kit/src/runtime/server/respond.js#L52`. While the implementation does a sufficient job in mitigating common CSRF attacks, the protection can be bypassed by simply specifying a different `Content-Type` header value.

### Details
The CSRF protection is implemented using the code shown below.

```js
const forbidden =
  // (1)
  request.method === 'POST' &&
  // (2)
  request.headers.get('origin') !== url.origin &&
  // (3)
  is_form_content_type(request);

if (forbidden) {
  // (4)
  const csrf_error = error(403, `Cross-site ${request.method} form submissions are forbidden`);
  if (request.headers.get('accept') === 'application/json') {
    return json(csrf_error.body, { status: csrf_error.status });
  }
  return text(csrf_error.body.message, { status: csrf_error.status });
}
```
If the incoming request specifies a POST method (1), the protection will compare the server’s origin with the value of the HTTP `Origin` header (2). A mismatch between these values signals that a potential attack has been detected. The final check is performed on the request’s `Content-Type` header (3) whether the value is either `application/x-www-form-urlencoded` or `multipart/form-data` (`kit/src/utils/http.js#L71`). If all the previous checks pass, the request will be rejected with an 403 error response (4).

The `is_form_content_type` validation is not sufficient to mitigate all possible variations of this type of attack. If a CSRF attack is performed with the `Content-Type` header set to `text/plain`, the protection will be circumvented and the request will be processed by the endpoint handler.
<!--
### PoC
To reproduce this issue, create and run a simple server (by default running on `localhost:3000`) with a POST endpoint handler such as:

```js
export async function POST({ request }) {
    const data = await request.json(); 
    console.log(JSON.stringify(data));
    return new Response(String('success'));
}
```

Next, save the malicious HTML page:

```html
<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1 id="name"></h1>
  <form action="http://localhost:3000/api/test" method="POST" enctype="text/plain">
    <input type="hidden" name="&#123;&quot;name&quot;&#58;&quot;test" value="&quot;&#44;&quot;age&quot;&#58;123&#125;" />
    <input type="submit" value="Submit" />
  </form>
</body>
</html>
```

in a file named `index.html`. Run another web server, using Python’s built in http.server module (`python -m http.server`, by default running on `localhost:8000`), navigate to [http://localhost:8000/index.html](http://localhost:8000/index.html) and click the `Submit` button. 

Verify that the browser’s URL has changed to `localhost:3000` and that the text `success` is displayed on the screen. Additionally, inspect the console of the SvelteKit web server and verify that the request body (`{"name":"test=","age":123}`) was parsed as valid JSON and printed out. 

It's worth noting that this attack is possible only for JSON request bodies. Form data sent using `text/plain` will be rejected by the server. 
-->
### Impact

If abused, this issue will allow malicious requests to be submitted from third-party domains, which can allow execution of operations within the context of the victim's session, and in extreme scenarios can lead to unauthorized access to users’ accounts.

### Remediation

SvelteKit 1.15.1 updates the `is_form_content_type` function call in the CSRF protection logic to include `text/plain`.

As additional hardening of the CSRF protection mechanism against potential method overrides, SvelteKit 1.15.1 is now performing validation on PUT, PATCH and DELETE methods as well. This latter hardening is only needed to protect users who have put in some sort of `?_method=` override feature themselves in their `handle` hook, so that the request that `resolve` sees could be `PUT`/`PATCH`/`DELETE` when the browser issues a `POST` request.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-5p75-vc5g-8rv2
- https://nvd.nist.gov/vuln/detail/CVE-2023-29003
- https://github.com/sveltejs/kit/commit/bb2253d51d00aba2e4353952d4fb0dcde6c77123
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fkit%401.15.1
