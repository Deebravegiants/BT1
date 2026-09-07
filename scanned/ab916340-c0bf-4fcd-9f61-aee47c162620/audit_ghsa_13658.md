# [M] LibreNMS vulnerable to rate limiting bypass on login page

## Summary
Severity: Medium
Advisory: GHSA-rq42-58qf-v3qx
CVE: CVE-2023-46745
CWE: CWE-307, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-rq42-58qf-v3qx
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <23.11.0

## Details
### Summary
Application is using two login methods and one of them is using GET request for authentication. There is no rate limiting security feature at GET request or backend is not validating that. 

### PoC
Go to /?username=admin&password=password&submit=
Capture request in Burpsuite intruder and add payload marker at password parameter value.
Start the attack after adding your password list
We have added 74 passwords
Check screenshot for more info
<img width="1241" alt="Screenshot 2023-11-06 at 8 55 19 PM" src="https://user-images.githubusercontent.com/31764504/280905148-42274f1e-f869-4145-95b4-71c0bffde3a0.png">

### Impact
An attacker can Bruteforce user accounts and using GET request for authentication is not recommended because certain web servers logs all requests in old logs which can also store victim user credentials.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-rq42-58qf-v3qx
- https://nvd.nist.gov/vuln/detail/CVE-2023-46745
- https://github.com/librenms/librenms/pull/15558
- https://github.com/librenms/librenms/commit/7c006e96251ae1d32e1a015b361a7bfbb815c028
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/23.11.0
