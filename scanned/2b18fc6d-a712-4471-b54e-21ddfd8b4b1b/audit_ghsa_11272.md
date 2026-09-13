# [M] AVideo vulnerable to IP Address Spoofing via Untrusted HTTP Headers in getRealIpAddr()

## Summary
Severity: Medium
Advisory: GHSA-8p2x-5cpm-qrqw
CVE: CVE-2026-33690
CWE: CWE-348
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8p2x-5cpm-qrqw
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `getRealIpAddr()` function in `objects/functions.php` trusts user-controlled HTTP headers to determine the client's IP address. 
An attacker can spoof their IP address by sending forged headers, bypassing any IP-based access controls or audit logging.

## Vulnerable Code

File: `objects/functions.php`
```php
$headers = [
    'HTTP_X_REAL_IP',      
    'HTTP_CLIENT_IP',    
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR'
];

foreach ($headers as $header) {
    if (!empty($_SERVER[$header])) {
        $ips = explode(',', $_SERVER[$header]);
        foreach ($ips as $ipCandidate) {
            $ipCandidate = trim($ipCandidate);
            if (filter_var($ipCandidate, FILTER_VALIDATE_IP, 
                           FILTER_FLAG_IPV4)) {
                return $ipCandidate; 
            }
        }
    }
}
```

## Attack Scenario

1. Attacker sends request with forged header:
```
X-Client-IP: 127.0.0.1
```
or
```
X-Real-IP: 192.168.1.1
```

2. `getRealIpAddr()` returns the forged IP
3. Any IP-based rate limiting, access control, or audit 
   log that relies on this function is bypassed

## Proof of Concept
```bash
curl -H "X-Client-IP: 127.0.0.1" \
     https://target.com/any_endpoint.php
```

The server now believes the request came from localhost.

## Impact
- Bypass IP-based rate limiting
- Bypass IP-based access controls
- Forge audit log entries
- Potential privilege escalation if localhost is trusted

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8p2x-5cpm-qrqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33690
- https://github.com/WWBN/AVideo/commit/1a1df6a9377e5cc67d1d0ac8ef571f7abbffbc6c
- https://github.com/WWBN/AVideo
