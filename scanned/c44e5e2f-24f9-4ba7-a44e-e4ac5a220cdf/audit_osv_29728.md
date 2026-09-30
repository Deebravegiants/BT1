# [M] OpenCTI leaks support information due to inadequate access control

## Summary
Severity: Medium
Advisory: CVE-2024-45805
Aliases: GHSA-42mm-c8x3-g5q6, PYSEC-2024-298
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-26
Source: https://osv.dev/vulnerability/CVE-2024-45805
Type: osv

## Details
OpenCTI is an open-source cyber threat intelligence platform. Before 6.3.0, general users can access information that can only be accessed by users with access privileges to admin and support information (SETTINGS_SUPPORT). This is due to inadequate access control for support information (http://<opencti_domain>/storage/get/support/UUID/UUID.zip), and that the UUID is available to general users using an attached query (logs query). This vulnerability is fixed in 6.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45805.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-42mm-c8x3-g5q6
- https://nvd.nist.gov/vuln/detail/CVE-2024-45805
