# [M] Named path parameters can be overridden in TrieRouter

## Summary
Severity: Medium
Advisory: GHSA-f6gv-hh8j-q8vq
CVE: CVE-2023-50710
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-f6gv-hh8j-q8vq
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <3.11.7

## Details
### Impact

The clients may override named path parameter values from previous requests if the application is using TrieRouter. So, there is a risk that a privileged user may use unintended parameters when deleting REST API resources.

TrieRouter is used either explicitly or when the application matches a pattern that is not supported by the default RegExpRouter.

The code to reproduce it. The server side application:

```ts
import { Hono } from 'hono'
import { TrieRouter } from 'hono/router/trie-router'

const wait = async (ms: number) => {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

const app = new Hono({ router: new TrieRouter() })

app.use('*', async (c, next) => {
  await wait(Math.random() * 200)
  return next()
})

app.get('/modules/:id/versions/:version', async (c) => {
  const id = c.req.param('id')
  const version = c.req.param('version')

  console.log('path', c.req.path)
  console.log('version', version)

  return c.json({
    id,
    version,
  })
})

export default app
```

The client code which makes requests to the server application:

```ts
const examples = [
  'http://localhost:8787/modules/first/versions/first',
  'http://localhost:8787/modules/second/versions/second',
  'http://localhost:8787/modules/third/versions/third',
]

const test = () => {
  for (const example of examples) {
    fetch(example)
      .then((response) => response.json())
      .then((data) => {
        const splitted = example.split('/')
        const expected = splitted[splitted.length - 1]

        if (expected !== data.version) {
          console.error(`Error: exprected ${expected} but got ${data.version} - url was ${example}`)
        }
      })
  }
}

test()
```

The results:

```txt
Error: exprected second but got third - url was http://localhost:8787/modules/second/versions/second
Error: exprected first but got third - url was http://localhost:8787/modules/first/versions/first
```

### Patches

"v3.11.7" includes the change to fix this issue.

### Workarounds

Don't use TrieRouter directly.

```ts
// DON'T USE TrieRouter
import { TrieRouter } from 'hono/router/trie-router'
const app = new Hono({ router: new TrieRouter() })
```

### References

Router options on the Hono website: https://hono.dev/api/hono#router-option

## References
- https://github.com/honojs/hono/security/advisories/GHSA-f6gv-hh8j-q8vq
- https://nvd.nist.gov/vuln/detail/CVE-2023-50710
- https://github.com/honojs/hono/commit/8e2b6b08518998783f66d31db4f21b1b1eecc4c8
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v3.11.7
