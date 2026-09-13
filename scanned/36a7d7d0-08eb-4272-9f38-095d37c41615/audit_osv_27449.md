# [C] Azure IPAM solution Elevation of Privilege Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-21638
Aliases: GHSA-m8mp-jq4c-g8j6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-01-10
Source: https://osv.dev/vulnerability/CVE-2024-21638
Type: osv

## Details
Azure IPAM (IP Address Management) is a lightweight solution developed on top of the Azure platform designed to help Azure customers manage their IP Address space easily and effectively. By design there is no write access to customers' Azure environments as the Service Principal used is only assigned the Reader role at the root Management Group level. Until recently, the solution lacked the validation of the passed in authentication token which may result in attacker impersonating any privileged user to access data stored within the IPAM instance and subsequently from Azure, causing an elevation of privilege. This vulnerability has been patched in version 3.0.0.

## References
- https://github.com/Azure/ipam/security/advisories/GHSA-m8mp-jq4c-g8j6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21638.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21638
- https://github.com/Azure/ipam/commit/64ef2d07edf16ffa50f29c7e0e25d32d974b367f
- https://github.com/Azure/ipam/pull/218
