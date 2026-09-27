# [C] AVideo has Plaintext Video Password Storage

## Summary
Severity: Critical
Advisory: GHSA-363v-5rh8-23wg
CVE: CVE-2026-33867
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-363v-5rh8-23wg
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

AVideo allows content owners to password-protect individual videos. The video password is stored in the database in **plaintext** — no hashing, salting, or encryption is applied. If an attacker gains read access to the database (via SQL injection, a database backup, or misconfigured access controls), they obtain all video passwords in cleartext.

### Details

**File:** `objects/video.php`

**Vulnerable setter:**
```php
public function setVideo_password($video_password)
{
    AVideoPlugin::onVideoSetVideo_password($this->id, $this->video_password, $video_password);
    $this->video_password = trim($video_password);
}
```

**Vulnerable getter:**
```php
public function getVideo_password()
{
    if (empty($this->video_password)) {
        return '';
    }
    return trim($this->video_password);
}
```

The value assigned to `$this->video_password` is only `trim()`-ed before being persisted to the database column `video_password` in the `videos` table. There is no call to any hashing function (e.g., `password_hash()`, `sha256`, or similar).

When a visitor enters a password to access a protected video, the comparison is done directly against the stored plaintext:
```php
// Comparison at access check:
if ($video->getVideo_password() === $_POST['password']) { ... }
```

This means:
1. Any database read (SQL injection, backup leak, hosting panel access) exposes all video passwords as cleartext.
2. Video passwords are often reused by users across other services, making this a credential harvesting risk.
3. The plaintext value is also present in application memory and any query logs.

### PoC

1. Set a password on any video via the AVideo admin/creator UI.
2. Query the database: `SELECT clean_title, video_password FROM videos WHERE video_password != '';`
3. All video passwords are returned in plaintext — no cracking required.

Alternatively, exploit any of the SQL injection vulnerabilities already reported in this repository to extract the `video_password` column directly.

### Impact

- **Type:** Cleartext Storage of Sensitive Information (CWE-312)
- **Severity:** High
- **Authentication required:** No — any database read access (including via SQL injection by unauthenticated users) exposes all passwords
- **Impact:** Full exposure of all video access passwords; credential reuse attacks against users who share passwords across services
- **Fix:** Hash video passwords on write using `password_hash($video_password, PASSWORD_BCRYPT)` and verify on read using `password_verify($_POST['password'], $stored_hash)`

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-363v-5rh8-23wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33867
- https://github.com/WWBN/AVideo/commit/f2d68d2adbf73588ea61be2b781d93120a819e36
- https://github.com/WWBN/AVideo
