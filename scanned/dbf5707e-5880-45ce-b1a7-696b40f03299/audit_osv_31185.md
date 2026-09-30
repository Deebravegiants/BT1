# [M] FoF Pretty Mail 1.1.2 Local File Inclusion via Email Template Settings

## Summary
Severity: Medium
Advisory: CVE-2024-58302
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2024-58302
Type: osv

## Details
FoF Pretty Mail 1.1.2 contains a local file inclusion vulnerability that allows administrative users to include arbitrary server files in email templates. Attackers can exploit the template settings by inserting file inclusion payloads to read sensitive system files like /etc/passwd during email generation.

## References
- https://flarum.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58302.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58302
- https://www.vulncheck.com/advisories/fof-pretty-mail-local-file-inclusion-via-email-template-settings
- https://github.com/FriendsOfFlarum/pretty-mail
- https://www.exploit-db.com/exploits/51947
