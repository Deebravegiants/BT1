# [H] CVE-2026-89161

## Summary
Severity: High
Advisory: CVE-2026-89161
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89161
Type: osv

## Details
In PCRE2 before 10.48, pcre2_jit_match mishandles a previously copied subject being passed in as a context. An incorrect free operation can occur.

## References
- https://github.com/PCRE2Project/pcre2/releases/tag/pcre2-10.48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89161.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-89161
- https://github.com/PCRE2Project/pcre2/pull/937
