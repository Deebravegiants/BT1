# [C] Coolify has a privilege escalation - low privileged user can invite themselves as an admin user

## Summary
Severity: Critical
Advisory: CVE-2025-64421
Aliases: GHSA-4p6r-m39m-9cm9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-64421
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In Coolify versions up to and including v4.0.0-beta.434, a low privileged user (member) can invite a high privileged user. At first, the application will throw an error, but if the attacker clicks the invite button a second time, it actually works. This way, a low privileged user can invite themselves as an administrator to the Coolify instance. After the high privileged user is invited, the attacker can initiate a password reset and log in with the new admin. As of time of publication, it is unclear if a patch is available.

## References
- https://drive.google.com/file/d/1YZHFgiZv_k9p9909A63DAErsTsh8K1rc/view?usp=drive_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64421.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-4p6r-m39m-9cm9
- https://nvd.nist.gov/vuln/detail/CVE-2025-64421
