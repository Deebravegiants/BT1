# [M] Denial of service through logs in zoneminder

## Summary
Severity: Medium
Advisory: CVE-2022-39291
Aliases: GHSA-cfcx-v52x-jh74
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-39291
Type: osv

## Details
ZoneMinder is a free, open source Closed-circuit television software application. Affected versions of zoneminder are subject to a vulnerability which allows users with "View" system permissions to inject new data into the logs stored by Zoneminder. This was observed through an HTTP POST request containing log information to the "/zm/index.php" endpoint. Submission is not rate controlled and could affect database performance and/or consume all storage resources. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- http://packetstormsecurity.com/files/171498/Zoneminder-Log-Injection-XSS-Cross-Site-Request-Forgery.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39291.json
- https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-cfcx-v52x-jh74
- https://nvd.nist.gov/vuln/detail/CVE-2022-39291
- https://github.com/ZoneMinder/zoneminder/commit/34ffd92bf123070cab6c83ad4cfe6297dd0ed0b4
- https://github.com/ZoneMinder/zoneminder/commit/73d9f2482cdcb238506388798d3cf92546f9e40c
- https://github.com/ZoneMinder/zoneminder/commit/cb3fc5907da21a5111ae54128a5d0b49ae755e9b
- https://github.com/ZoneMinder/zoneminder/commit/de2866f9574a2bf2690276fad53c91d607825408
