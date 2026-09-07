# [H] fetch: Authorization headers not dropped when redirecting cross-origin

## Summary
Severity: High
Advisory: GHSA-f27p-cmv8-xhm6
CVE: CVE-2025-21620
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-06
Source: https://github.com/advisories/GHSA-f27p-cmv8-xhm6
Type: github-advisory

## Affected
- crates.io: `deno_fetch` — affected >=0.0.1 <0.204.0
- crates.io: `deno` — affected >=0
- crates.io: `deno` — affected >=2.0.0 <2.1.2

## Details
### Summary
When you send a request with the `Authorization` header to one domain, and the response asks to redirect to a different domain, Deno's`fetch()` redirect handling creates a follow-up redirect request that keeps the original `Authorization` header, leaking its content to that second domain.


### Details

The [right behavior](https://fetch.spec.whatwg.org/#ref-for-cors-non-wildcard-request-header-name) would be to drop the `Authorization` header instead, in this scenario. The same is generally applied to `Cookie` and `Proxy-Authorization` headers, and is done for not only host changes, but also protocol/port changes. Generally referred to as "origin".

The [documentation](https://docs.deno.com/runtime/reference/web_platform_apis/#:~:text=Deno%20does%20not%20follow%20the,leaking%20authenticated%20data%20cross%20origin.) states: 
> Deno does not follow the same-origin policy, because the Deno user agent currently does not have the concept of origins, and it does not have a cookie jar. This means Deno **does not need** to protect against leaking authenticated data cross origin 

### Reproduction
```ts
const ac = new AbortController()

const server1 = Deno.serve({ port: 3001, signal: ac.signal }, (req) => {
  return new Response(null, {
    status: 302,
    headers: {
      'location': 'http://localhost:3002/redirected'
    },
  })
})

const server2 = Deno.serve({ port: 3002, signal: ac.signal }, (req) => {
  const body = JSON.stringify({
    url: req.url,
    hasAuth: req.headers.has('authorization'),
  })
  return new Response(body, {
    status: 200,
    headers: {'content-type': 'application/json'},
  })
})

async function main() {
  const response = await fetch("http://localhost:3001/", {
    headers: {authorization: 'Bearer foo'}
  })
  const body = await response.json()
  
  ac.abort()
  
  if (body.hasAuth) {
    console.error('ERROR: Authorization header should not be present after cross-origin redirect')
  } else {
    console.log('SUCCESS: Authorization header is not present after cross-origin redirect')
  }
}

setTimeout(main, 500)
```

## References
- https://github.com/denoland/deno/security/advisories/GHSA-f27p-cmv8-xhm6
- https://nvd.nist.gov/vuln/detail/CVE-2025-21620
- https://github.com/denoland/deno
