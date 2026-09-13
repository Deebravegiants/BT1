# [H] Path traversal in Jumpserver

## Summary
Severity: High
Advisory: CVE-2023-42819
Aliases: GHSA-ghg2-2whp-6m33
CVSS: 8.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-42819
Type: osv

## Details
JumpServer is an open source bastion host. Logged-in users can access and modify the contents of any file on the system. A user can use the 'Job-Template' menu and create a playbook named 'test'. Get the playbook id from the detail page, like 'e0adabef-c38f-492d-bd92-832bacc3df5f'. An attacker can exploit the directory traversal flaw using the provided URL to access and retrieve the contents of the file. `https://jumpserver-ip/api/v1/ops/playbook/e0adabef-c38f-492d-bd92-832bacc3df5f/file/?key=../../../../../../../etc/passwd` a similar method to modify the file content is also present. This issue has been addressed in version 3.6.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42819.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-ghg2-2whp-6m33
- https://nvd.nist.gov/vuln/detail/CVE-2023-42819
- https://github.com/jumpserver/jumpserver/commit/d0321a74f1713d031560341c8fd0a1859e6510d8
