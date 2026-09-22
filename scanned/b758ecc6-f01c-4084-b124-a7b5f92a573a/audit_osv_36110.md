# [H] CVE-2026-20884

## Summary
Severity: High
Advisory: CVE-2026-20884
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-20884
Type: osv

## Details
An integer overflow vulnerability exists in the deflate_dng_load_raw functionality of LibRaw Commit 8dc68e2. A specially crafted malicious file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2364
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2364
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/20xxx/CVE-2026-20884.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-20884
