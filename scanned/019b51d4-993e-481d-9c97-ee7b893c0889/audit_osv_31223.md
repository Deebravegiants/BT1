# [C] Missing Authorization in Conduit

## Summary
Severity: Critical
Advisory: CVE-2024-6303
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-6303
Type: osv

## Details
Missing authorization in Client-Server API in Conduit <=0.7.0, allowing for any alias to be removed and added to another room, which can be used for privilege escalation by moving the #admins alias to a room which they control, allowing them to run commands resetting passwords, siging json with the server's key, deactivating users, and more

## References
- https://conduit.rs/changelog/#v0-8-0-2024-06-12
- https://gitlab.com/famedly/conduit/-/releases/v0.8.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6303.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6303
