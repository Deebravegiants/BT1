# [H] Cyberduck and Mountain Duck - Improper Certificate Store Handling

## Summary
Severity: High
Advisory: CVE-2025-41255
Aliases: GHSA-vjjc-grpp-m655
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-41255
Type: osv

## Details
Cyberduck and Mountain Duck improperly handle TLS certificate pinning for untrusted certificates (e.g., self-signed), unnecessarily installing it to the Windows Certificate Store of the current user without any restrictions.











This issue affects Cyberduck through 9.1.6 and Mountain Duck through 4.17.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41255.json
- https://github.com/iterate-ch/cyberduck/security/advisories/GHSA-vjjc-grpp-m655
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250325-01_Cyberduck_Mountain_Duck_Certificate_Handling
- https://nvd.nist.gov/vuln/detail/CVE-2025-41255
- https://github.com/iterate-ch/cyberduck
