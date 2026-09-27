# [C] Knowage Server vulnerable to path traversal via upload functionality

## Summary
Severity: Critical
Advisory: CVE-2023-38702
Aliases: GHSA-7mjh-73q3-c3fc
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-38702
Type: osv

## Details
Knowage is an open source analytics and business intelligence suite. Starting in the 6.x.x branch and prior to version 8.1.8, the endpoint `/knowage/restful-services/dossier/importTemplateFile` allows authenticated users to upload `template file` on the server, but does not need any authorization to be reached. When the JSP file is uploaded, the attacker just needs to connect to `/knowageqbeengine/foo.jsp` to gain code execution on the server. By exploiting this vulnerability, an attacker with low privileges can upload a JSP file to the `knowageqbeengine` directory and gain code execution capability on the server. This issue has been patched in Knowage version 8.1.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38702.json
- https://github.com/KnowageLabs/Knowage-Server/security/advisories/GHSA-7mjh-73q3-c3fc
- https://nvd.nist.gov/vuln/detail/CVE-2023-38702
