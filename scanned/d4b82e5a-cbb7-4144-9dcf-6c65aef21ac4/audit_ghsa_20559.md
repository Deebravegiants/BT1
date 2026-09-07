# [M] Insufficient Session Expiration in Pterodactyl API

## Summary
Severity: Medium
Advisory: GHSA-7v3x-h7r2-34jv
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-7v3x-h7r2-34jv
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.7.0

## Details
### Impact
A vulnerability exists in Pterodactyl Panel `<= 1.6.6` that could allow a malicious attacker that compromises an API key to generate an authenticated user session that is not revoked when the API key is deleted, thus allowing the malicious user to remain logged in as the user the key belonged to.

It is important to note that **a malicious user must first compromise an existing API key for a user to exploit this issue**. It cannot be exploited by chance, and requires a coordinated attack against an individual account using a known API key.

### Patches
This issue has been addressed in the `v1.7.0` release of Pterodactyl Panel.

### Workarounds
Those not wishing to upgrade may apply the change below:

```diff
diff --git a/app/Http/Middleware/Api/AuthenticateKey.php b/app/Http/Middleware/Api/AuthenticateKey.php
index eb25dac6..857bfab2 100644
--- a/app/Http/Middleware/Api/AuthenticateKey.php
+++ b/app/Http/Middleware/Api/AuthenticateKey.php
@@ -70,7 +70,7 @@ class AuthenticateKey
         } else {
             $model = $this->authenticateApiKey($request->bearerToken(), $keyType);

-            $this->auth->guard()->loginUsingId($model->user_id);
+            $this->auth->guard()->onceUsingId($model->user_id);
         }
```

### For more information
If you have any questions or comments about this advisory please reach out to `Tactical Fish#8008` on [Discord](https://discord.gg/pterodactyl) or email `dane@pterodactyl.io`.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-7v3x-h7r2-34jv
- https://github.com/pterodactyl/panel/commit/dfa329ddf242908b60e22e3340ea36359eab1ef4
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.7.0
