# [M] CVE-2026-76957

## Summary
Severity: Medium
Advisory: CVE-2026-76957
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-76957
Type: osv

## Details
libexpat before 2.8.4 lacks handler call depth tracking with custom encoding callbacks. Thus, a use-after-free can occur. NOTE: this is similar to CVE-2026-50219, CVE-2026-56131 and CVE-2026-56412.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76957.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76957
- https://github.com/libexpat/libexpat/pull/1322
- https://github.com/libexpat/libexpat/pull/1329
