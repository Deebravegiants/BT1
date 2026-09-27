# [H] CVE-2020-25788

## Summary
Severity: High
Advisory: CVE-2020-25788
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-19
Source: https://osv.dev/vulnerability/CVE-2020-25788
Type: osv

## Details
An issue was discovered in Tiny Tiny RSS (aka tt-rss) before 2020-09-16. imgproxy in plugins/af_proxy_http/init.php mishandles $_REQUEST["url"] in an error message.

## References
- https://community.tt-rss.org/t/heads-up-several-vulnerabilities-fixed/3799
- https://git.tt-rss.org/fox/tt-rss/commit/c3d14e1fa54c7dade7b1b7955575e2991396d7ef
- https://blog.neagaru.com/p/exploiting-tiny-tiny-rss-2020
