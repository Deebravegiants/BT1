# [H] Coolify has host header injection in forgot password

## Summary
Severity: High
Advisory: CVE-2025-64425
Aliases: GHSA-f737-2p93-g2cw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-64425
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. In Coolify versions up to and including v4.0.0-beta.434, an attacker can initiate a password reset for a victim, and modify the host header of the request to a malicious value. The victim will receive a password reset email, with a link to the malicious host. If the victim clicks this link, their reset token is sent to the attacker's server, allowing the attacker to use it to change the victim's password and takeover their account. As of time of publication, it is unclear if a patch is available.

## References
- https://drive.google.com/file/d/1I5sJHcpetJbKlwVS2usAD7qmgH37Y4rw/view?usp=drive_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64425.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-f737-2p93-g2cw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64425
