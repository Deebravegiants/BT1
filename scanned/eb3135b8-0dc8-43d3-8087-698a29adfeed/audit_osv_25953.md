# [H] Nextcloud Server users can make external storage mount points inaccessible for other users

## Summary
Severity: High
Advisory: CVE-2023-48239
Aliases: GHSA-f962-hw26-g267
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-48239
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 25.0.0 and prior to versions 25.0.13, 26.0.8, and 27.1.3 of Nextcloud Server and starting in version 20.0.0 and prior to versions 20.0.14.16, 21.0.9.13, 22.2.10.15, 23.0.12.12, 24.0.12.8, 25.0.13, 26.0.8, and 27.1.3 of Nextcloud Enterprise Server, a malicious user could update any personal or global external storage, making them inaccessible for everyone else as well. Nextcloud Server 25.0.13, 26.0.8, and 27.1.3 and Nextcloud Enterprise Server is upgraded to 20.0.14.16, 21.0.9.13, 22.2.10.15, 23.0.12.12, 24.0.12.8, 25.0.13, 26.0.8, and 27.1.3 contain a patch for this issue. As a workaround, disable app files_external. This workaround also makes the external storage inaccessible but retains the configurations until a patched version has been deployed.

## References
- https://hackerone.com/reports/2212627
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48239.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-f962-hw26-g267
- https://nvd.nist.gov/vuln/detail/CVE-2023-48239
- https://github.com/nextcloud/server/pull/41123
