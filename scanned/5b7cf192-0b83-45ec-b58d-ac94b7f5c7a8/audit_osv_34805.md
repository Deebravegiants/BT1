# [H] CVE-2025-65203

## Summary
Severity: High
Advisory: CVE-2025-65203
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-65203
Type: osv

## Details
KeePassXC-Browser thru 1.9.9.2 autofills or prompts to fill stored credentials into documents rendered under a browser-enforced CSP directive and iframe attribute sandbox, allowing attacker-controlled script in the sandboxed document to access populated form fields and exfiltrate credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65203.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65203
- https://github.com/keepassxreboot/keepassxc-browser/issues/2647
- https://github.com/keepassxreboot/keepassxc-browser/pull/2648
