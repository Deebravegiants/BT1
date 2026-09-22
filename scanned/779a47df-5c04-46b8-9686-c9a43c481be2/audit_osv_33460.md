# [C] SWUpdate Untrusted Script Execution via Signed Update TOCTOU

## Summary
Severity: Critical
Advisory: CVE-2025-41259
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2025-41259
Type: osv

## Details
SWUpdate before 2026.05 is affected by a time-of-check time-of-use (TOCTOU) race condition that allows local unprivileged attackers to escalate privileges to root or install untrusted contents using a signed update.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/41xxx/CVE-2025-41259.json
- https://github.com/sbaresearch/advisories/tree/public/2025/SBA-ADV-20251206-01_SWUpdate_Untrusted_Script_Execution_via_Signed_Update_TOCTOU
- https://nvd.nist.gov/vuln/detail/CVE-2025-41259
- https://github.com/sbabic/swupdate/commit/f4bd64260e233e207354d68d572b1cbc3e63689d
- https://github.com/sbabic/swupdate
