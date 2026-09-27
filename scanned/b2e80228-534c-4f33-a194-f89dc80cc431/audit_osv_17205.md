# [H] CVE-2020-13694

## Summary
Severity: High
Advisory: CVE-2020-13694
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-01
Source: https://osv.dev/vulnerability/CVE-2020-13694
Type: osv

## Details
In QuickBox Community Edition through 2.5.5 and Pro Edition through 2.1.8, the local www-data user can execute sudo mysql without a password, which means that the www-data user can execute arbitrary OS commands via the mysql -e option.

## References
- https://s1gh.sh/cve-2020-13448-quickbox-authenticated-rce/
