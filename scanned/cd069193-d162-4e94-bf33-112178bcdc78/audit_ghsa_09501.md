# [H] Grav Vulnerable to Publisher-Level Stored XSS via Unquoted Event Attributes

## Summary
Severity: High
Advisory: GHSA-9695-8fr9-hw5q
CVE: CVE-2026-42612
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-9695-8fr9-hw5q
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability in `getgrav/grav` allows publisher-level accounts to execute arbitrary JavaScript. The issue arises from a blacklist bypass in the `detectXss()` function when handling unquoted HTML event attributes.

### Details
The `detectXss()` function relies on a blacklist pattern to filter malicious attributes. The specific regex pattern used to match `on*` events is flawed:
```php
'on_events' => '#(<[^>]+[a-z\x00-\x20\"\'\/])(on[a-z]+|xmlns)\s*=[\s|\'\"].*[\s|\'\"]>#iUu'
```
This pattern fails to properly identify `on*` event handlers that are constructed without quotation marks. This allows an attacker to completely bypass the filter. *Note: It is highly recommended to replace this blacklist approach with a robust, established HTML sanitization library.*

### PoC
An attacker with publisher-level access can reproduce this by injecting the following payload into any vulnerable content field:
```html
<img src=x onerror=eval(atob(/YWxlcnQoZG9jdW1lbnQuY29va2llKQ/.source))>
```
<img width="1889" height="482" alt="image1" src="https://github.com/user-attachments/assets/0f1a339b-25a8-4b6e-91af-8c59e6a39297" />
<img width="3055" height="920" alt="image2" src="https://github.com/user-attachments/assets/12680058-bbb3-4446-b58e-515533bb4e90" />
<img width="2909" height="1339" alt="image3" src="https://github.com/user-attachments/assets/c7ed7e61-8dcf-402d-8589-98d18978c71a" />


**Execution Details:**
The `onerror` event is written without quotes to bypass the regex. Because unquoted attributes are restricted in their character usage (e.g., the `=` symbol cannot be used easily), the payload leverages `atob()` and regex `.source` to decode the base64 string `YWxlcnQoZG9jdW1lbnQuY29va2llKQ` (which translates to `alert(document.cookie)`). The `atob()` function conveniently auto-completes the necessary `=` padding for the base64 string.

### Impact
- **Vulnerability Type:** Stored Cross-Site Scripting (XSS)
- **Impacted Parties:** Any user (including administrators) who views the compromised content published by the attacker.
- **Consequences:** Attackers can execute malicious scripts in a victim's browser, leading to session hijacking (cookie theft), unauthorized actions.


---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`5a12f9be8`](https://github.com/getgrav/grav/commit/5a12f9be8) — will ship in **2.0.0-beta.2**.

**What changed:** the `on_events` regex in `Security::detectXss()` no longer requires quotes or whitespace around `=`. The previous form:

```
'on_events' => '#(<[^>]+[\s\x00-\x20\"\'\/])(on\s*[a-z]+|xmlns)\s*=[\s|\'\"].*[\s|\'\"]>#iUu'
```

required `[\s|'"]` immediately after the `=`, so `<img src=x onerror=alert(1)>` slid past. The new regex drops the value-matching tail entirely and just flags the presence of an `on*=` attribute anywhere inside a tag:

```
'on_events' => '#<[^>]*?[\s\x00-\x20\"\'\/](on\s*[a-z]+|xmlns)\s*=#iu'
```

Detecting the attribute name + `=` is enough for a tripwire — the trade-off is occasional false positives on legitimate attribute *values* containing `on*=` substrings, which the maintainer can hand-approve.

This same regex bypass was the detection-layer half of GHSA-c2q3-p4jr-c55f and GHSA-w8cg-7jcj-4vv2; the fix here knocks both down.

**Files:**
- [`system/src/Grav/Common/Security.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Security.php).
- [`tests/unit/Grav/Common/Security/DetectXssTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/DetectXssTest.php) — 18 cases: unquoted PoCs, quoted-form regression, safe-content negatives.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-9695-8fr9-hw5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-42612
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
