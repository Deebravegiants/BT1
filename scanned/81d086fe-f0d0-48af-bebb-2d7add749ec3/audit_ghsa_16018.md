# [H] SPEmailHandler-PHP has Potential Abuse for Sending Arbitrary Emails

## Summary
Severity: High
Advisory: GHSA-mj5r-x73q-fjw6
CVE: CVE-2024-53860
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-mj5r-x73q-fjw6
Type: github-advisory

## Affected
- Packagist: `spencer14420/sp-php-email-handler` — affected >=0 <1.0.0

## Details
### Impact
Messages sent using this script are vulnerable to abuse, as the script allows anybody to specify arbitrary email recipients and include user-provided content in confirmation emails. This could enable malicious actors to use your server to send spam, phishing emails, or other malicious content, potentially damaging your domain's reputation and leading to blacklisting by email providers.

### Patches
Patched in version 1.0.0 by removing user-provided content from confirmation emails. All pre-release versions (alpha and beta) are vulnerable to this issue and should not be used.

### Workarounds
There are no workarounds for this issue. Users must upgrade to version 1.0.0 to mitigate the vulnerability.

## References
- https://github.com/Spencer14420/SPEmailHandler-PHP/security/advisories/GHSA-mj5r-x73q-fjw6
- https://nvd.nist.gov/vuln/detail/CVE-2024-53860
- https://github.com/Spencer14420/SPEmailHandler-PHP/commit/6f00dd0d44ff27889aed2980a5ba06e60d83549d
- https://github.com/Spencer14420/SPEmailHandler-PHP
