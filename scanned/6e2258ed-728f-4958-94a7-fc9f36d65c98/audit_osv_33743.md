# [H] Apache Traffic Server: Remote DoS via memory exhaustion in ESI Plugin

## Summary
Severity: High
Advisory: CVE-2025-49763
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-49763
Type: osv

## Details
ESI plugin does not have the limit for maximum inclusion depth, and that allows excessive memory consumption if malicious instructions are inserted.

Users can use a new setting for the plugin (--max-inclusion-depth) to limit it.
This issue affects Apache Traffic Server: from 10.0.0 through 10.0.5, from 9.0.0 through 9.2.10.

Users are recommended to upgrade to version 9.2.11 or 10.0.6,  which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49763.json
- https://lists.apache.org/thread/15t32nxbypqg1m2smp640vjx89o6v5f8
- https://nvd.nist.gov/vuln/detail/CVE-2025-49763
