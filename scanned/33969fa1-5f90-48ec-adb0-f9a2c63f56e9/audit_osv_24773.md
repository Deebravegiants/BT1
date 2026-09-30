# [C] Scope of workflow operations is not validated in nextcloud server

## Summary
Severity: Critical
Advisory: CVE-2023-26482
Aliases: GHSA-h3c9-cmh8-7qpj
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/CVE-2023-26482
Type: osv

## Details
Nextcloud server is an open source home cloud implementation. In affected versions a missing scope validation allowed users to create workflows which are designed to be only available for administrators. Some workflows are designed to be RCE by invoking defined scripts, in order to generate PDFs, invoking webhooks or running scripts on the server. Due to this combination depending on the available apps the issue can result in a RCE at the end. It is recommended that the Nextcloud Server is upgraded to 24.0.10 or 25.0.4. Users unable to upgrade should disable app `workflow_scripts` and `workflow_pdf_converter` as a mitigation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26482.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-h3c9-cmh8-7qpj
- https://nvd.nist.gov/vuln/detail/CVE-2023-26482
- https://github.com/nextcloud/server/commit/5a06b50b10cc9278bbe68bbf897a0c4aeb0c4e60
