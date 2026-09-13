# [C] WWBN AVideo Unauthenticated Path Traversal via notify.ffmpeg.json.php

## Summary
Severity: Critical
Advisory: CVE-2026-86189
Aliases: GHSA-cprx-fggj-7vpq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86189
Type: osv

## Details
WWBN AVideo contains a path traversal vulnerability in notify.ffmpeg.json.php that allows unauthenticated attackers to write files to arbitrary locations by supplying a caller-chosen path in the avideoRelativePath parameter. Attackers can replay any previously issued ciphertext as a notifyCode token, which is decrypted but never validated, to bypass authentication and write files to the application root and subdirectories.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86189.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-cprx-fggj-7vpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-86189
- https://www.vulncheck.com/advisories/wwbn-avideo-unauthenticated-path-traversal-via-notify-ffmpeg-json-php
