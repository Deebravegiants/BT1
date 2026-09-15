# [H] ZoneMinder vulnerable to OS Command injection in daemonControl() API

## Summary
Severity: High
Advisory: CVE-2023-26039
Aliases: GHSA-44q8-h2pw-cc9g
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26039
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application for Linux which supports IP, USB and Analog cameras. Versions prior to 1.36.33 and 1.37.33 contain an OS Command Injection via daemonControl() in (/web/api/app/Controller/HostController.php). Any authenticated user can construct an api command to execute any shell command as the web user. This issue is patched in versions 1.36.33 and 1.37.33.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26039.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-44q8-h2pw-cc9g
- https://nvd.nist.gov/vuln/detail/CVE-2023-26039
