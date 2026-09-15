# [H] Cyberduck and Mountain Duck - Weak Hash Algorithm for Certificate Fingerprint

## Summary
Severity: High
Advisory: CVE-2025-41256
Aliases: GHSA-688c-vjrc-84rv
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-06-25
Source: https://osv.dev/vulnerability/CVE-2025-41256
Type: osv

## Details
Cyberduck and Mountain Duck improper handle TLS certificate pinning for untrusted certificates (e.g., self-signed), since the certificate fingerprint is stored as SHA-1, although SHA-1 is considered weak.







This issue affects Cyberduck: through 9.1.6; Mountain Duck: through 4.17.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41256.json
- https://github.com/iterate-ch/cyberduck/security/advisories/GHSA-688c-vjrc-84rv
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20250325-02_Cyberduck_Mountain_Duck_Weak_Hash
- https://nvd.nist.gov/vuln/detail/CVE-2025-41256
- https://github.com/iterate-ch/cyberduck
