# [H] CVE-2022-30708

## Summary
Severity: High
Advisory: CVE-2022-30708
CVSS: 8.8 (CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:L/S:U/UI:N)
Published: 2022-05-15
Source: https://osv.dev/vulnerability/CVE-2022-30708
Type: osv

## Details
Webmin through 1.991, when the Authentic theme is used, allows remote code execution when a user has been manually created (i.e., not created in Virtualmin or Cloudmin). This occurs because settings-editor_write.cgi does not properly restrict the file parameter.

## References
- https://github.com/esp0xdeadbeef/rce_webmin/blob/main/exploit.py
- https://webmin.com/changes.html
- https://www.twitch.tv/videos/1483029790
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30708.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30708
- https://github.com/webmin/webmin/issues/1635
- https://github.com/webmin/webmin/commit/6a2334bf8b27d55c7edf0b2825cd14f3f8a69d4d
- https://github.com/esp0xdeadbeef/rce_webmin
- https://github.com/webmin/authentic-theme/releases
- https://github.com/webmin/webmin/releases
