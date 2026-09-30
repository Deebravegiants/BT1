# [M] CVE-2021-26595

## Summary
Severity: Medium
Advisory: CVE-2021-26595
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-26595
Type: osv

## Details
In Directus 8.x through 8.8.1, an attacker can learn sensitive information such as the version of the CMS, the PHP version used by the site, and the name of the DBMS, simply by view the result of the api-aa, called automatically upon a connection. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- https://github.com/sgranel/directusv8
