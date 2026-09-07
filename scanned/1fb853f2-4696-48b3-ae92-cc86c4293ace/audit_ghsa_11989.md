# [M] AVideo has Unauthenticated PGP Message Decryption via Public Endpoint

## Summary
Severity: Medium
Advisory: GHSA-5x2w-37xf-7962
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5x2w-37xf-7962
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

The AVideo platform exposes a publicly accessible endpoint that performs server-side PGP decryption without requiring any form of authentication. Any anonymous user can submit a private key, ciphertext, and passphrase to the endpoint and receive the decrypted plaintext in the JSON response. This functionality is entirely unprotected, meaning no session, token, or credential is needed to invoke it.

### Details

The endpoint at decryptMessage.json.php accepts a JSON body containing three user-supplied fields: a private key, an encrypted message, and a key password. The server passes these directly into a decryption routine and returns the result. There is no call to any authentication or session validation function before this operation is performed. The relevant server-side operation is:

```php
$textDecrypted = decryptMessage($obj->textToDecrypt, $obj->privateKeyToDecryptMsg, $obj->keyPassword);
```

Because no access control exists, any unauthenticated request that reaches this endpoint will be processed. The primary concerns are exposure of private key material to server memory and logging infrastructure, and unconstrained consumption of server CPU resources for cryptographic operations. An attacker who has obtained a private key and matching ciphertext through other means can offload decryption work to the target server without holding any account on the platform.

### PoC

```sh
curl -s -X POST \
  "https://target.example.com/plugin/LoginControl/pgp/decryptMessage.json.php" \
  -H "Content-Type: application/json" \
  -d '{
    "textToDecrypt": "-----BEGIN PGP MESSAGE-----\n<base64_ciphertext>\n-----END PGP MESSAGE-----",
    "privateKeyToDecryptMsg": "-----BEGIN PGP PRIVATE KEY BLOCK-----\n<base64_private_key>\n-----END PGP PRIVATE KEY BLOCK-----",
    "keyPassword": "passphrase"
  }'
```

### Impact

Private key material submitted to this endpoint is processed in server memory and may be captured in application logs, web server access logs, or error logs depending on server configuration. This can result in unintended disclosure of sensitive key material to administrators or anyone with log access. Additionally, the lack of any rate limiting combined with the absence of authentication allows any external party to submit large volumes of decryption requests, consuming server CPU resources without restriction. Any user who can reach the endpoint network-layer can trigger these effects.

### Mitigation

A User::isLogged() check, or an equivalent session and authentication validation step, should be added at the top of decryptMessage.json.php before any user-supplied input is processed. Decryption operations should only be permitted for authenticated and authorized users. Server logging configuration should also be reviewed to ensure that POST body contents, including key material, are not written to persistent logs.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5x2w-37xf-7962
- https://github.com/WWBN/AVideo
