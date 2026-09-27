# [H] CVE-2026-38820

## Summary
Severity: High
Advisory: CVE-2026-38820
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-38820
Type: osv

## Details
openNDS before 11.0.0 is susceptible to unauthenticated OS command execution via shell command injection through the fas query parameter on the /opennds_preauth/ endpoint because of libopennds.sh.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38820.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38820
- https://github.com/openNDS/openNDS/commit/8c03750d9a17d601fa7bd03ae7cde20c7c8d1252
