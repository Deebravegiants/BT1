# [C] Magento Patch SUPEE-10752 - Multiple security enhancements vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-prpf-cj87-hwvr
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-prpf-cj87-hwvr
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <1.9.3.9

## Details
Magento Commerce 1.14.3.9 and Open Source 1.9.3.9 bring essential security enhancements with Patch SUPEE-10752. These updates address various vulnerabilities, including authenticated Admin user remote code execution (RCE), cross-site request forgery (CSRF), and more.

Key Security Improvements:

- APPSEC-2001: Authenticated Remote Code Execution (RCE) using custom layout XML
- APPSEC-2015: Authenticated Remote Code Execution (RCE) through the Create New Order feature (Commerce only)
- APPSEC-2042: PHP Object Injection and RCE in the Magento admin panel (Commerce Target Rule module)
- APPSEC-2029: PHP Object Injection and Remote Code Execution (RCE) in the Admin panel (Commerce)
- APPSEC-2007: Authenticated SQL Injection when saving a category
- APPSEC-2027: CSRF is possible against Web sites, Stores, and Store Views
- APPSEC-1882: The cron.php file can leak database credentials
- APPSEC-2006: Stored cross-site scripting (XSS) through the Enterprise Logging extension
- APPSEC-2005: Persistent Cross-Site Scripting (XSS) injection in Configuration table
- APPSEC-1880: Cross-Site Scripting (XSS) through the Admin Username in the CMS Revision Editor (Commerce only)
- APPSEC-2004: Cross-Site Scripting (XSS) through Remote File Inclusion
- APPSEC-1988: Path traversal vulnerability in templates
- APPSEC-1987: Reflective cross-site scripting (XSS) through filter manipulation
- APPSEC-2034: XSS in Admin Create Order Configure Product Via Compatible File Extensions
- APPSEC-1876: Cross-site scripting (XSS) in Admin Bundle Product Bundle Items Tab through Product SKU
- APPSEC-1874: Cross-Site Scripting (XSS) in the Admin Gift Registry Type Edit via Attribute Group
- APPSEC-1872: Cross-Site Scripting (XSS) in the Admin Manage Catalog Events list through category name
- APPSEC-1928: Stored XSS in Downloadable Product Links title - frontend
- APPSEC-1871: Cross-Site Scripting (XSS) in the Admin Manage Customer Rewards points history using the Reason field
- APPSEC-1870: Cross-Site Scripting (XSS) in Admin Manage Invitations list through Invitee email address
- APPSEC-1972/APPSEC-2103: Admin password change does not force the logout of the Admin user
- APPSEC-1934: Systemic Cross-Site Request Forgery (CSRF) on the Checkout page
- APPSEC-1917: Password theft though uploaded video and Auth Prompt password theft vulnerability
- APPSEC-1993: IP spoofing

Patches and upgrades are available for the following Magento versions:

- Magento Commerce 1.9.0.0-1.14.3.9: SUPEE-10752 or upgrade to Magento Commerce 1.14.3.9.
- Magento Open Source 1.5.0.0-1.9.3.9: SUPEE-10752 or upgrade to Magento Open Source 1.9.3.9.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/magento1ce/2018-06-29.yaml
- https://github.com/magento/magento2
- https://magento.com/security/patches/supee-10752
