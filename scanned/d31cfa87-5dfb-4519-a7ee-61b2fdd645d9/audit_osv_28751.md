# [H] CVE-2024-36070

## Summary
Severity: High
Advisory: CVE-2024-36070
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-36070
Type: osv

## Details
tine before 2023.11.8, when an LDAP backend is used, allows anonymous remote attackers to obtain sensitive authentication information via setup.php because of getRegistryData in Setup/Frontend/Json.php. (An update is also available for the 2022.11 series.)

## References
- https://github.com/tine-groupware/tine/releases/tag/2023.11.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36070.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36070
- https://github.com/tine-groupware/tine/commit/5d556a1225aa358cbf7cfbeae518c9386b46f516
