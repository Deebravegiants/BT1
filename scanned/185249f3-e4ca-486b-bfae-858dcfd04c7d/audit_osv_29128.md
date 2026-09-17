# [H] CVE-2024-39924

## Summary
Severity: High
Advisory: CVE-2024-39924
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-39924
Type: osv

## Details
An issue was discovered in Vaultwarden (formerly Bitwarden_RS) 1.30.3. A vulnerability has been identified in the authentication and authorization process of the endpoint responsible for altering the metadata of an emergency access. It permits an attacker with granted emergency access to escalate their privileges by changing the access level and modifying the wait time. Consequently, the attacker can gain full control over the vault (when only intended to have read access) while bypassing the necessary wait period.

## References
- https://github.com/dani-garcia/vaultwarden/blob/1.30.3/src/api/core/emergency_access.rs#L115-L148
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.32.0
- https://www.mgm-sp.com/cve/missing-authentication-check-for-emergency-access
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39924.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39924
