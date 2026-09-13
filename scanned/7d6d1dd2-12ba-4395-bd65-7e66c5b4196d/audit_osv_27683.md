# [M] 1Panel set-cookie is missing the Secure keyword

## Summary
Severity: Medium
Advisory: CVE-2024-24768
Aliases: GHSA-9xfw-jjq2-7v8h, GO-2024-2531
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24768
Type: osv

## Details
1Panel is an open source Linux server operation and maintenance management panel. The HTTPS cookie that comes with the panel does not have the Secure keyword, which may cause the cookie to be sent in plain text if accessed using HTTP. This issue has been patched in version 1.9.6.

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-9xfw-jjq2-7v8h
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24768.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24768
- https://github.com/1Panel-dev/1Panel/commit/1169648162c4b9b48e0b4aa508f9dea4d6bc50d5
- https://github.com/1Panel-dev/1Panel/pull/3817
