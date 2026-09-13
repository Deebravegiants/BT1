# [H] CVE-2021-26593

## Summary
Severity: High
Advisory: CVE-2021-26593
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-26593
Type: osv

## Details
In Directus 8.x through 8.8.1, an attacker can see all users in the CMS using the API /users/{id}. For each call, they get in response a lot of information about the user (such as email address, first name, and last name) but also the secret for 2FA if one exists. This secret can be regenerated. NOTE: This vulnerability only affects products that are no longer supported by the maintainer

## References
- https://github.com/sgranel/directusv8
