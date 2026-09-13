# [H] CVE-2026-57589

## Summary
Severity: High
Advisory: CVE-2026-57589
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57589
Type: osv

## Details
sys/kern/sysv_sem.c in OpenBSD through 7.9 has a use-after-free allowing local privilege escalation to root. This is a context switch use-after-free after tsleep in sys_semget().

## References
- https://openai.com/index/patch-the-planet/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57589.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57589
- https://github.com/openbsd/src/commit/1957873d2063db11dab780eca75b5e629d1e838d
