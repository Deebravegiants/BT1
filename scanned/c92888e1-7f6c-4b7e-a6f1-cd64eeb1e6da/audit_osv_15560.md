# [H] CVE-2019-17199

## Summary
Severity: High
Advisory: CVE-2019-17199
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-05
Source: https://osv.dev/vulnerability/CVE-2019-17199
Type: osv

## Details
www/getfile.php in WPO WebPageTest 19.04 on Windows allows Directory Traversal (for reading arbitrary files) because of an unanchored regular expression, as demonstrated by the a.jpg\.. substring.

## References
- https://github.com/WPO-Foundation/webpagetest/pull/1299
