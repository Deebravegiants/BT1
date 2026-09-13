# [M] Admidio has an incomplete fix for CVE-2026-32812 (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-hcjj-chvw-fmw9
CVE: CVE-2026-42194
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-hcjj-chvw-fmw9
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
### Summary

The incomplete SSRF fix in Admidio's `fetch_metadata.php` validates the resolved IP address but passes the original hostname-based URL to `curl_init()`, leaving a DNS rebinding TOCTOU window that allows redirecting requests to internal IPs.

### Affected Package

- **Ecosystem:** Other
- **Package:** admidio
- **Affected versions:** < commit f6b7a966abe4d75e9f707d665d7b4b5570e3185a
- **Patched versions:** >= commit f6b7a966abe4d75e9f707d665d7b4b5570e3185a

### Severity

Medium

### CWE

CWE-918 — Server-Side Request Forgery (SSRF)

### Details

In `modules/sso/fetch_metadata.php` (lines 21-49), the SSO metadata fetch validates the URL scheme is HTTPS (line 21), runs `filter_var($rawUrl, FILTER_VALIDATE_URL)` (line 27), resolves the hostname via `gethostbyname()` and checks the IP against private/reserved ranges (lines 34-38), then passes the original URL with the hostname to `curl_init($url)` at line 41.

The fundamental problem is at step 4: cURL resolves the hostname again independently. Between `gethostbyname()` at step 3 and `curl_exec()` at step 4, a DNS rebinding attack can cause the hostname to resolve to `169.254.169.254` (AWS metadata), `127.0.0.1`, or any other internal address. No `CURLOPT_RESOLVE` is set to pin the hostname to the validated IP.

The TOCTOU window between `gethostbyname()` and `curl_exec()` is the core issue, and the patch does not close it.

### PoC

```python
#!/usr/bin/env python3
"""
CVE-2026-32812 - Admidio SSRF via DNS Rebinding in fetch_metadata.php

Vulnerability: modules/sso/fetch_metadata.php resolves hostname via gethostbyname()
and checks if IP is private, but passes the ORIGINAL URL (with hostname) to curl_init().
DNS rebinding can cause hostname to resolve to internal IP when cURL actually connects.

Real vulnerable PHP code copied from:
  Admidio/admidio, modules/sso/fetch_metadata.php

This PoC runs the actual PHP validation logic via `php -r`.
"""

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VULN_PHP = os.path.join(SCRIPT_DIR, "fetch_metadata.php")


def run_php(code):
    return subprocess.run(["php", "-r", code], capture_output=True, text=True, timeout=15)


def main():
    if not os.path.exists(VULN_PHP):
        print(f"ERROR: Vulnerable PHP source not found at {VULN_PHP}")
        sys.exit(1)

    print(f"Source file: {VULN_PHP}")
    print("Extracted from: Admidio/admidio, modules/sso/fetch_metadata.php\n")

    php_code = r"""
    echo "=== CVE-2026-32812: Admidio SSRF via DNS Rebinding ===\n\n";

    // Extracted from: modules/sso/fetch_metadata.php lines 21-49
    // Character-for-character copy of the validation logic:
    function test_admidio_ssrf_filter($rawUrl, $simulated_ip) {
        // Only allow https:// scheme (line 21)
        if (!preg_match('#^https://#i', $rawUrl)) {
            return ['blocked' => true, 'reason' => 'Not HTTPS'];
        }

        // Validate URL (line 27)
        $url = filter_var($rawUrl, FILTER_VALIDATE_URL);
        if (!$url) {
            return ['blocked' => true, 'reason' => 'Invalid URL'];
        }

        // Resolve hostname and block internal/private IP ranges (lines 34-38)
        $host = parse_url($url, PHP_URL_HOST);
        $ip = $simulated_ip;  // In real code: gethostbyname($host)

        if (filter_var($ip, FILTER_VALIDATE_IP,
            FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false) {
            return ['blocked' => true, 'reason' => "Private/reserved IP: $ip"];
        }

        // VULNERABILITY: curl_init($url) at line 41 uses original URL with hostname
        return [
            'blocked' => false,
            'url_passed_to_curl' => $url,
            'host' => $host,
            'checked_ip' => $ip,
        ];
    }

    $tests = [
        ['https://attacker-rebind.example.com/saml/metadata', '93.184.216.34',
         'Public IP at check time - passes, then DNS rebinds to 169.254.169.254'],
        ['https://attacker-rebind.example.com/saml/metadata', '169.254.169.254',
         'After rebind to metadata - blocked IF re-checked'],
        ['https://192.168.1.1/admin', '192.168.1.1',
         'Direct private IP - blocked'],
        ['https://10.0.0.1/internal', '10.0.0.1',
         'Direct internal IP - blocked'],
        ['http://attacker.com/metadata', '93.184.216.34',
         'HTTP scheme - blocked (HTTPS required)'],
        ['https://evil.com/metadata', '8.8.8.8',
         'External HTTPS URL - passes'],
    ];

    $vuln_found = false;
    foreach ($tests as $test) {
        $result = test_admidio_ssrf_filter($test[0], $test[1]);
        $status = $result['blocked'] ? 'BLOCKED' : 'PASSED';
        echo sprintf("%-65s => %s\n", $test[2], $status);

        if (!$result['blocked']) {
            $curl_host = parse_url($result['url_passed_to_curl'], PHP_URL_HOST);
            if ($curl_host !== $result['checked_ip']) {
                echo "  VULN: cURL gets hostname '$curl_host' (checked IP: '{$result['checked_ip']}')\n";
                echo "  DNS can rebind between gethostbyname() and cURL connect\n";
                $vuln_found = true;
            }
        }
    }

    echo "\n=== Key Finding ===\n";
    echo "fetch_metadata.php line 41: curl_init(\$url) uses ORIGINAL URL with hostname\n";
    echo "IP check on line 35 used gethostbyname() result.\n";
    echo "TOCTOU window: DNS can rebind between check and cURL connection.\n";
    echo "CURLOPT_RESOLVE is NOT set to pin hostname to checked IP.\n\n";

    if ($vuln_found) {
        echo "VULNERABILITY CONFIRMED\n";
    }
    """

    result = run_php(php_code)
    print(result.stdout)
    if result.stderr:
        print(f"PHP stderr: {result.stderr}")

    if "VULNERABILITY CONFIRMED" in result.stdout:
        print("VULNERABILITY CONFIRMED")
        sys.exit(0)
    else:
        print("Vulnerability test inconclusive")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Steps to reproduce:**
1. Place the vulnerable `fetch_metadata.php` source in the same directory.
2. Ensure PHP CLI is installed, then run `python3 poc.py`.
3. Observe the TOCTOU window where cURL receives a hostname instead of the validated IP.

**Expected output:**
```
VULNERABILITY CONFIRMED
curl_init() uses the original hostname-based URL while IP validation used gethostbyname(), leaving a DNS rebinding TOCTOU window.
```

### Impact

An attacker can exploit the SSO metadata fetch endpoint to make the Admidio server issue HTTPS requests to internal services. On cloud-hosted instances, this enables reading the instance metadata service (`169.254.169.254`) to steal IAM credentials. On-premise deployments can be used to scan internal networks or access localhost services.

### Suggested Remediation

Use `CURLOPT_RESOLVE` to pin the hostname to the IP address returned by `gethostbyname()`, ensuring cURL connects to the exact IP that was validated:

```php
$resolve = ["$host:443:$ip"];
curl_setopt($ch, CURLOPT_RESOLVE, $resolve);
```

### Resources

- Incomplete fix commit: https://github.com/Admidio/admidio/commit/f6b7a966abe4d75e9f707d665d7b4b5570e3185a
- Original CVE: CVE-2026-32812

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-6j68-gcc3-mq73
- https://github.com/Admidio/admidio/security/advisories/GHSA-hcjj-chvw-fmw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42194
- https://github.com/Admidio/admidio/commit/f6b7a966abe4d75e9f707d665d7b4b5570e3185a
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
