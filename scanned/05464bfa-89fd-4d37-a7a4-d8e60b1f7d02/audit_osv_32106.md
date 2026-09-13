# [H] vaultwarden allows RCE in the admin panel

## Summary
Severity: High
Advisory: CVE-2025-24364
Aliases: GHSA-h6cc-rc6q-23j4
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2025-24364
Type: osv

## Details
vaultwarden is an unofficial Bitwarden compatible server written in Rust, formerly known as bitwarden_rs. Attacker with authenticated access to the vaultwarden admin panel can execute arbitrary code in the system. The attacker could then change some settings to use sendmail as mail agent but adjust the settings in such a way that it would use a shell command. It then also needed to craft a special favicon image which would have the commands embedded to run during for example sending a test email. This vulnerability is fixed in 1.33.0.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.33.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24364.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-h6cc-rc6q-23j4
- https://nvd.nist.gov/vuln/detail/CVE-2025-24364
