# [C] CVE-2017-9426

## Summary
Severity: Critical
Advisory: CVE-2017-9426
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-26
Source: https://osv.dev/vulnerability/CVE-2017-9426
Type: osv

## Details
ws.php in the Facetag extension 0.0.3 for Piwigo allows SQL injection via the imageId parameter in a facetag.changeTag or facetag.listTags action.

## References
- http://touhidshaikh.com/blog/poc/facetag-extension-piwigo-sqli/
- https://www.exploit-db.com/exploits/42094/
- https://www.youtube.com/watch?v=MVCe_zYtFsQ
