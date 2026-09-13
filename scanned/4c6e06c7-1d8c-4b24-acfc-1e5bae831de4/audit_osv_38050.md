# [M] Xerte Online Toolkits Missing Authentication via connector.php

## Summary
Severity: Medium
Advisory: CVE-2026-34413
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-34413
Type: osv

## Details
Xerte Online Toolkits versions 3.15 and earlier contain a missing authentication vulnerability in the elFinder connector endpoint at /editor/elfinder/php/connector.php where an HTTP redirect to unauthenticated callers does not call exit() or die(), allowing PHP execution to continue and process the full request server-side. Unauthenticated attackers can perform file operations on project media directories including creating directories, uploading files, renaming files, duplicating files, overwriting files, and deleting files, which can be chained with path traversal and extension blocklist vulnerabilities to achieve remote code execution and arbitrary file read.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34413
- https://www.vulncheck.com/advisories/xerte-online-toolkits-missing-authentication-via-connector-php
- https://xerte.org.uk/xertetoolkits_3.15_ChangeLog.html
- https://github.com/thexerteproject/xerteonlinetoolkits/issues/1527
- https://xerte.org.uk/index.php/en/downloads-1/category/3-xerte-online-toolkits
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/02661be88cc369325ea01b508086bde7fbfec805
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/17e4f945fe6a3400fa88c01eda18c1075ee4a212
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/507d55c5e91bf9310b5b1c7fad8aebfef902ad23
- https://github.com/thexerteproject/xerteonlinetoolkits
- https://github.com/bootstrapbool/xerteonlinetoolkits-rce
