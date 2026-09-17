# [H] xmlseclibs: Missing AES-GCM Authentication Tag Validation on Encrypted Nodes Allows for Unauthorized Decryption

## Summary
Severity: High
Advisory: GHSA-4v26-v6cg-g6f9
CVE: CVE-2026-32313
CWE: CWE-354
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-4v26-v6cg-g6f9
Type: github-advisory

## Affected
- Packagist: `robrichards/xmlseclibs` — affected >=0 <3.1.5

## Details
### Summary
XML nodes encrypted with either aes-128-gcm, aes-192-gcm, or aes-256-gcm lack validation of the authentication tag length.
An attacker can use this to brute-force an authentication tag, recover the [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of), and decrypt the encrypted nodes.
It also allows to forge arbitrary ciphertexts without knowing the encryption key.

### Details
When decrypting with either aes-128-gcm, aes-192-gcm, or aes-256-gcm [here](https://github.com/robrichards/xmlseclibs/blob/2bdfd742624d739dfadbd415f00181b4a77aaf07/src/XMLSecurityKey.php#L467-L479), the `$authTag` is set from a `substr()`, but never has its length validated (it should be validated with something like `strlen($authTag) == self::AUTHTAG_LENGTH`).
For that reason, a shorter than expected data blob will allow for the `$authTag` to have as short a tag as only one byte (see [PHP's documentation](https://www.php.net/manual/en/function.openssl-decrypt.php#:~:text=The%20length%20of%20the%20tag%20is%20not%20checked%20by%20the%20function.%20It%20is%20the%20caller%27s%20responsibility%20to%20ensure%20that%20the%20length%20of%20the%20tag%20matches%20the%20length%20of%20the%20tag%20retrieved%20when%20openssl_encrypt()%20has%20been%20called.%20Otherwise%20the%20decryption%20may%20succeed%20if%20the%20given%20tag%20only%20matches%20the%20start%20of%20the%20proper%20tag.)).

See this example:
```php
function test($data) {
    $ivSize = 12;
    $tagSize = 16;

    $iv = substr($data, 0, $ivSize);
    $data = substr($data, $ivSize);
    $offset = 0 - $tagSize;
    $tag = substr($data, $offset);
    $ct = substr($data, 0, $offset);

    echo 'IV: "' . $iv . '"' . PHP_EOL;
    echo 'Tag: "' . $tag . '"' . PHP_EOL;
    echo 'CT: "' . $ct . '"' . PHP_EOL;
}

/* Outputs:
php > test('myNonceNoncet');
IV: "myNonceNonce"
Tag: "t"
CT: ""
php > test('myNonceNonceta');
IV: "myNonceNonce"
Tag: "ta"
CT: ""
php > test('myNonceNoncetag');
IV: "myNonceNonce"
Tag: "tag"
CT: ""
*/
```

With a legit ciphertext in hand, this is enough to recover the [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of).
With that key, any authenticated tags can be computed offline which allows for decryption of the ciphertext and forgery of arbitrary ciphertexts.

### PoC
1. Setup a server expecting XML with an encrypted assertion
    - Run this php script [poc.php](https://github.com/user-attachments/files/24426600/poc.php.txt) with `php -S 127.0.0.1:8888` (taken from [this saml test case](https://github.com/robrichards/xmlseclibs/blob/69fd63080bc47a8d51bc101c30b7cb756862d1d6/tests/saml/saml-decrypt.phpt#L62))
    - The script expects this private key: [sp-private-key.pem.](https://github.com/user-attachments/files/24426620/sp-private-key.pem.txt)
2. Create an XML document with an encrypted assertion (encrypted with `aes-256-gcm`)
    - Here is the `SAMLResponse` used in the video below: [saml_response.txt](https://github.com/user-attachments/files/24426638/saml_response.txt)

**Note:** The steps from 3 to 6 are implemented in this exploit script: [nonce_reuse_with_fmt_val_oracle.py](https://github.com/user-attachments/files/24426645/nonce_reuse_with_fmt_val_oracle.py).
You can run the script with `sage -python nonce_reuse_with_fmt_val_oracle.py -s 'url-encoded_and_base64-encoded_samlresponse'`

3. Take the content of the `<xenc:CipherValue>` node and apply the following modifications
    1. Base64-decode the content
    2. Take the first 12 bytes and save them as the nonce
    3. Take the last 16 bytes and save them as the tag
    4. Now brute-force the tag of an empty ciphertext
        1. Loop through all 256 possible byte values (let's call that `byte_tag_attempt`)
        2. Concatenate together the nonce and the `byte_tag_attempt`
        3. Base64-encode the result
        4. Replace the content of the `<xenc:CipherValue>` node with this result
        5. On http errors 500, we learn that the tag is valid
        6. Do the same for the next byte of the tag until all 16 bytes have been brute-forced
4. With this new tag and the empty ciphertext, compute the [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of) (the way to do this has been described in this [blog post](https://frereit.de/aes_gcm/))
5. Use this [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of) to compute authentication tags offline for arbitrary ciphertexts
6. Decryption is done by observing XML parsing errors that occur after modifying the ciphertext, those can be seen as http errors 500

[poc.webm](https://github.com/user-attachments/assets/2f6e4a7e-4384-4350-b423-7ddd77aa9152)


### Impact
The general impact is:
- XML nodes encrypted with AES-GCM can be decrypted by observing parsing differences
- XML nodes encrypted with AES-GCM can be modified to decrypt to an arbitrary value
- The GCM internal [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of) can be recovered

In cases where the encryption key is embedded in the XML and is encrypted with the Service Provider's public key (like often done with SAML), the last two items don't have a big impact.
This is because: 
- With the Service Provider's public key, an arbitrary ciphertext can be created with a known symmetric key
- The symmetric keys are generated on the fly every time the IdP creates a new `SAMLResponse`

In any case, secrets that are embedded in the XML, whether coming from an IdP, or from another scheme, can be decrypted.

**Important:** If static symmetric keys are used, as the [GHASH key](https://en.wikipedia.org/wiki/Galois/Counter_Mode#:~:text=%29%20is%20the-,hash%20key,-%2C%20a%20string%20of) could have leaked, you must rotate those keys.

### References
For additional information on the issue, you can refer to this [blog post](https://sideni.xyz/posts/exploiting_openssl_api/) about the OpenSSL issue and how it can be exploited.

## References
- https://github.com/robrichards/xmlseclibs/security/advisories/GHSA-4v26-v6cg-g6f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32313
- https://github.com/robrichards/xmlseclibs/commit/03062be78178cbb5e8f605cd255dc32a14981f92
- https://github.com/robrichards/xmlseclibs
- https://github.com/robrichards/xmlseclibs/releases/tag/3.1.5
