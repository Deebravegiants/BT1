# [C] su-exec through 0.3 Privilege Escalation via Numeric User ID

## Summary
Severity: Critical
Advisory: CVE-2026-82457
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82457
Type: osv

## Details
su-exec through 0.3 fails to validate numeric user and group identifiers parsed with strtol before assigning to uid_t and gid_t, allowing truncation of out-of-range values to zero. Attackers can supply large numeric identifiers that truncate to root's identifier, causing su-exec to execute target programs with root privileges instead of intended unprivileged accounts.

## References
- https://gist.github.com/thesmartshadow/ed96e2a88643c34a247c9b7cf9e311be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82457
- https://www.vulncheck.com/advisories/su-exec-through-0.3-privilege-escalation-via-numeric-user-id
- https://github.com/ncopa/su-exec
- https://github.com/ncopa/su-exec/blob/89c016e6e08749d583efdeda04b9f73e1218e253/su-exec.c
