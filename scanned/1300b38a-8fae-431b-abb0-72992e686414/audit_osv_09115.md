# [H] CVE-2016-7964

## Summary
Severity: High
Advisory: CVE-2016-7964
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-10-31
Source: https://osv.dev/vulnerability/CVE-2016-7964
Type: osv

## Details
The sendRequest method in HTTPClient Class in file /inc/HTTPClient.php in DokuWiki 2016-06-26a and older, when media file fetching is enabled, has no way to restrict access to private networks. This allows users to scan ports of internal networks via SSRF, such as 10.0.0.1/8, 172.16.0.0/12, and 192.168.0.0/16.

## References
- http://www.securityfocus.com/bid/94245
- https://github.com/splitbrain/dokuwiki/issues/1708
