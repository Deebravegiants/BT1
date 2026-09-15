# [H] CVE-2021-28128

## Summary
Severity: High
Advisory: CVE-2021-28128
Aliases: GHSA-37hx-4mcq-wc3h
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2021-28128
Type: osv

## Details
In Strapi through 3.6.0, the admin panel allows the changing of one's own password without entering the current password. An attacker who gains access to a valid session can use this to take over an account by changing the password.

## References
- https://github.com/strapi/strapi/releases
- https://strapi.io/changelog
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2021-008.txt
