# [H] FOG Sensitive Information Disclosure

## Summary
Severity: High
Advisory: CVE-2024-41108
Aliases: GHSA-p3f9-4jj4-fm2g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-41108
Type: osv

## Details
FOG is a free open-source cloning/imaging/rescue suite/inventory management system. The hostinfo page has missing/improper access control since only the host's mac address is required to obtain the configuration information. This data can only be retrieved if a task is pending on that host. Otherwise, an error message containing "Invalid tasking!" will be returned. The domainpassword in the hostinfo dump is hidden even to authenticated users, as it is displayed as a row of asterisks when navigating to the host's Active Directory settings.  This vulnerability is fixed in 1.5.10.41.

## References
- https://github.com/FOGProject/fogproject/blob/a4bb1bf39ac53c3cbe623576915fbc3b5c80a00f/packages/web/service/hostinfo.php
- https://github.com/FOGProject/fogproject/blob/a4bb1bf39ac53c3cbe623576915fbc3b5c80a00f/packages/web/service/hostname.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41108.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-p3f9-4jj4-fm2g
- https://nvd.nist.gov/vuln/detail/CVE-2024-41108
