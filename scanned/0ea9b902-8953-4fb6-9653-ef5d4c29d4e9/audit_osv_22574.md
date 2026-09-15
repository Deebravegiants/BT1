# [C] Gin-vue-admin - Unrestricted File Upload

## Summary
Severity: Critical
Advisory: CVE-2022-32176
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-32176
Type: osv

## Details
In "Gin-Vue-Admin", versions v2.5.1 through v2.5.3b are vulnerable to Unrestricted File Upload that leads to execution of javascript code, through the "Compress Upload" functionality to the Media Library. When an admin user views the uploaded file, a low privilege attacker will get access to the admin's cookie leading to account takeover.

## References
- https://github.com/flipped-aurora/gin-vue-admin/blob/v2.5.3beta/web/src/components/upload/image.vue#L43-L49
- https://www.mend.io/vulnerability-database/CVE-2022-32176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32176.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32176
