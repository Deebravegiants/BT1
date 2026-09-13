# [M] CVE-2025-59031

## Summary
Severity: Medium
Advisory: CVE-2025-59031
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2025-59031
Type: osv

## Details
Dovecot has provided a script to use for attachment to text conversion. This script unsafely handles zip-style attachments. Attacker can use specially crafted OOXML documents to cause unintended files on the system to be indexed and subsequently ending up in FTS indexes. Do not use the provided script, instead, use something else like FTS tika. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59031.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59031
