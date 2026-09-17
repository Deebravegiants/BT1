# [M] pgAgent scheduled batch job scripts are created in a predictable temporary directory potentially allowing a denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-0218
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0218
Type: osv

## Details
When batch jobs are executed by pgAgent, a script is created in a temporary directory and then executed. In versions of pgAgent prior to 4.2.3, an insufficiently seeded random number generator is used when generating the directory name, leading to the possibility for a local attacker to pre-create the directory and thus prevent pgAgent from executing jobs, disrupting scheduled tasks.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00018.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0218.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0218
- https://github.com/pgadmin-org/pgagent/commit/1ecd193a2be3a3dc9e98f369495e1a792e6d508c
