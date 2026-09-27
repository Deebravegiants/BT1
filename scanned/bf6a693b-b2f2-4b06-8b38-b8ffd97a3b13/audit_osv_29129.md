# [M] CVE-2024-39925

## Summary
Severity: Medium
Advisory: CVE-2024-39925
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-39925
Type: osv

## Details
An issue was discovered in Vaultwarden (formerly Bitwarden_RS) 1.30.3. It lacks an offboarding process for members who leave an organization. As a result, the shared organization key is not rotated when a member departs. Consequently, the departing member, whose access should be revoked, retains a copy of the organization key. Additionally, the application fails to adequately protect some encrypted data stored on the server. Consequently, an authenticated user could gain unauthorized access to encrypted data of any organization, even if the user is not a member of the targeted organization. However, the user would need to know the corresponding organizationId. Hence, if a user (whose access to an organization has been revoked) already possesses the organization key, that user could use the key to decrypt the leaked data.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.32.0
- https://www.mgm-sp.com/cve/missing-rotation-of-the-organization-key
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39925.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39925
- https://github.com/dani-garcia/vaultwarden/releases
