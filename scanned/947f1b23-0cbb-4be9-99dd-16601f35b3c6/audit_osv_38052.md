# [C] Xerte Online Toolkits File Upload RCE via elfinder Connector

## Summary
Severity: Critical
Advisory: CVE-2026-34415
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-34415
Type: osv

## Details
Xerte Online Toolkits versions 3.15 and earlier contain an incomplete input validation vulnerability in the elFinder connector endpoint that fails to block PHP-executable extensions .php4 due to an incorrect regex pattern. Unauthenticated attackers can exploit this flaw combined with authentication bypass and path traversal vulnerabilities to upload malicious PHP code, rename it with a .php4 extension, and execute arbitrary operating system commands on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34415.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34415
- https://www.vulncheck.com/advisories/xerte-online-toolkits-file-upload-rce-via-elfinder-connector
- https://xerte.org.uk/xertetoolkits_3.15_ChangeLog.html
- https://github.com/thexerteproject/xerteonlinetoolkits/issues/1527
- https://xerte.org.uk/index.php/en/downloads-1/category/3-xerte-online-toolkits
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/02661be88cc369325ea01b508086bde7fbfec805
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/17e4f945fe6a3400fa88c01eda18c1075ee4a212
- https://github.com/thexerteproject/xerteonlinetoolkits/commit/507d55c5e91bf9310b5b1c7fad8aebfef902ad23
- https://github.com/thexerteproject/xerteonlinetoolkits
- https://github.com/bootstrapbool/xerteonlinetoolkits-rce
