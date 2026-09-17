# [H] Xibo CMS vulnerable to Remote Code Execution through Zip Slip

## Summary
Severity: High
Advisory: CVE-2023-33177
Aliases: GHSA-jj27-x85q-crqv
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33177
Type: osv

## Details
Xibo is a content management system (CMS). A path traversal vulnerability exists in the Xibo CMS whereby a specially crafted zip file can be uploaded to the CMS via the layout import function by an authenticated user which would allow creation of files outside of the CMS library directory as the webserver user. This can be used to upload a PHP webshell inside the web root directory and achieve remote code execution as the webserver user. Users should upgrade to version 2.3.17 or 3.3.5, which fix this issue. Customers who host their CMS with Xibo Signage have already received an upgrade or patch to resolve this issue regardless of the CMS version that they are running.

## References
- https://claroty.com/team82/disclosure-dashboard
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33177.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-jj27-x85q-crqv
- https://nvd.nist.gov/vuln/detail/CVE-2023-33177
- https://xibosignage.com/blog/security-advisory-2023-05/
- https://github.com/xibosignage/xibo-cms/commit/1cbba380fa751a00756e70d7b08b5c6646092658
- https://github.com/xibosignage/xibo-cms/commit/45c6b53c3978639db03b63270a56f4397f49b2c9
