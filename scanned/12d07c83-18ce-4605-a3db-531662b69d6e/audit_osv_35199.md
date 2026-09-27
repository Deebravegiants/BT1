# [H] Wget2: gnu wget2: memory corruption and crash via filename sanitization logic with attacker-controlled urls

## Summary
Severity: High
Advisory: CVE-2025-69195
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-01-09
Source: https://osv.dev/vulnerability/CVE-2025-69195
Type: osv

## Details
A flaw was found in GNU Wget2. This vulnerability, a stack-based buffer overflow, occurs in the filename sanitization logic when processing attacker-controlled URL paths, particularly when filename restriction options are active. A remote attacker can exploit this by providing a specially crafted URL, which, upon user interaction with wget2, can lead to memory corruption. This can cause the application to crash and potentially allow for further malicious activities.

## References
- https://access.redhat.com/security/cve/CVE-2025-69195
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69195.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69195
- https://bugzilla.redhat.com/show_bug.cgi?id=2425770
- https://gitlab.com/gnuwget/wget2
