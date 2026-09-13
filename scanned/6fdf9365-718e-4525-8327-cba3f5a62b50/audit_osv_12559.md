# [H] CVE-2018-12909

## Summary
Severity: High
Advisory: CVE-2018-12909
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-27
Source: https://osv.dev/vulnerability/CVE-2018-12909
Type: osv

## Details
Webgrind 1.5 relies on user input to display a file, which lets anyone view files from the local filesystem (that the webserver user has access to) via an index.php?op=fileviewer&file= URI. NOTE: the vendor indicates that the product is not intended for a "publicly accessible environment.

## References
- https://github.com/jokkedk/webgrind/issues/112
