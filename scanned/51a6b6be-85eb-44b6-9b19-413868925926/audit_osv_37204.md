# [M] Apache OFBiz: Low-Privilege SSTI Leading to RCE in the Content Component

## Summary
Severity: Medium
Advisory: CVE-2026-29207
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-29207
Type: osv

## Details
Improper Neutralization of Special Elements Used in a Template Engine vulnerability in Apache OFBiz.

This issue affects Apache OFBiz: before 24.09.06.

Users are recommended to upgrade to version 24.09.06, which fixes the issue.

Please note that in the updated version, "Data Resource" records with dataTemplateTypeId = "FTL" are no longer supported.

Additionally, in the updated version, the "Ecommerce Customer" security group no longer includes content management grants. Users are advised to remove these permissions from any production site as well.

## References
- http://www.openwall.com/lists/oss-security/2026/05/19/14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29207.json
- https://lists.apache.org/thread/3rcrp8bh3x6ovrj5xnc0fm1f0nrn52r0
- https://nvd.nist.gov/vuln/detail/CVE-2026-29207
