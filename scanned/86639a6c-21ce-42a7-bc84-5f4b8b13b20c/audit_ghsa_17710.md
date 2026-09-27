# [M] Guzzle OAuth Subscriber has insufficient nonce entropy

## Summary
Severity: Medium
Advisory: GHSA-237r-r8m4-4q88
CVE: CVE-2025-21617
CWE: CWE-338
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-06
Source: https://github.com/advisories/GHSA-237r-r8m4-4q88
Type: github-advisory

## Affected
- Packagist: `guzzlehttp/oauth-subscriber` — affected >=0 <0.8.1

## Details
### Impact

Nonce generation does not use sufficient entropy nor a cryptographically secure pseudorandom source (https://github.com/guzzle/oauth-subscriber/blob/0.8.0/src/Oauth1.php#L192). This can leave servers vulnerable to replay attacks when TLS is not used.

### Patches

Upgrade to version 0.8.1 or higher.

### Workarounds

No.

### References

Issue is similar to https://nvd.nist.gov/vuln/detail/CVE-2025-22376.

## References
- https://github.com/guzzle/oauth-subscriber/security/advisories/GHSA-237r-r8m4-4q88
- https://nvd.nist.gov/vuln/detail/CVE-2025-21617
- https://github.com/guzzle/oauth-subscriber/commit/92b619b03bd21396e51c62e6bce83467d2ce8f53
- https://github.com/FriendsOfPHP/security-advisories/blob/master/guzzlehttp/oauth-subscriber/CVE-2025-21617.yaml
- https://github.com/guzzle/oauth-subscriber
- https://github.com/guzzle/oauth-subscriber/blob/0.8.0/src/Oauth1.php#L192
- https://github.com/guzzle/oauth-subscriber/releases/tag/0.8.1
