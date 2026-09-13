# [M] CVE-2022-37034

## Summary
Severity: Medium
Advisory: CVE-2022-37034
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-02-01
Source: https://osv.dev/vulnerability/CVE-2022-37034
Type: osv

## Details
In dotCMS 5.x-22.06, it is possible to call the TempResource multiple times, each time requesting the dotCMS server to download a large file. If done repeatedly, this will result in Tomcat request-thread exhaustion and ultimately a denial of any other requests.

## References
- https://www.dotcms.com/security/SI-65
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37034.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37034
