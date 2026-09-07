# [C] Magento Open Source Security Advisory: Patch SUPEE-10975

## Summary
Severity: Critical
Advisory: GHSA-cv25-3pxr-4q7x
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-cv25-3pxr-4q7x
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=1.9.0.0 <1.14.4.0

## Details
Magento Commerce 1.14.4.0 and Open Source 1.9.4.0 have been enhanced with critical security updates to address multiple vulnerabilities, including remote code execution (RCE), cross-site scripting (XSS), cross-site request forgery (CSRF), and more. The following issues have been identified and remediated:

- PRODSECBUG-1589: Stops Brute Force Requests via basic RSS authentication
- MAG-23: M1 Credit Card Storage Capability
- PRODSECBUG-2149: Authenticated RCE using customer import
- PRODSECBUG-2159: API Based RCE Vulnerability
- PRODSECBUG-2156: RCE Via Unauthorized Upload
- PRODSECBUG-2155: Authenticated RCE using dataflow
- PRODSECBUG-2053: Prevents XSS in Newsletter Template
- PRODSECBUG-2142: XSS in CMS Preview
- PRODSECBUG-1860: Admin Account XSS Attack Cessation via Filename
- PRODSECBUG-2119: EE Patch to include names in templates
- PRODSECBUG-2129: XSS in Google Analytics Vulnerability
- PRODSECBUG-2019: Merchant Wishlist Security Strengthening
- PRODSECBUG-2104: Send to a Friend Vulnerability
- PRODSECBUG-2125: CSRF on deletion of Blocks Vulnerability
- PRODSECBUG-2088: CSRF Vulnerability related to Customer Group Deletion
- PRODSECBUG-2140: CSRF on deletion of Site Map
- PRODSECBUG-2108: Outdated jQuery causing PCI scanning failures
- MAG-12, MAG-2: Encryption Keys Stored in Plain Text
- PRODSECBUG-2141: Unauthorized Admin Panel Bypass

### Patching and Upgrading:
Patches and upgrades are available for the following Magento versions:

Magento Commerce 1.9.0.0-1.14.4.0: Apply SUPEE-10975 or upgrade to Magento Commerce 1.14.4.0.
Magento Open Source 1.5.0.0-1.9.4.0: Apply SUPEE-10975 or upgrade to Magento Open Source 1.9.4.0.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ee/2018-11-28.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/supee-10975
- https://web.archive.org/web/20210517140123/https://magento.com/security/patches/supee-10975
