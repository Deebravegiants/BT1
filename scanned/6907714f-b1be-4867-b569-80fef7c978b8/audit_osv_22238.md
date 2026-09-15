# [H] CVE-2022-23950

## Summary
Severity: High
Advisory: CVE-2022-23950
Aliases: GHSA-9r9r-f8xc-m875
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-23950
Type: osv

## Details
In Keylime before 6.3.0, Revocation Notifier uses a fixed /tmp path for UNIX domain socket which can allow unprivileged users a method to prohibit keylime operations.

## References
- https://seclists.org/oss-sec/2022/q1/101
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23950.json
- https://github.com/keylime/keylime/security/advisories/GHSA-9r9r-f8xc-m875
- https://nvd.nist.gov/vuln/detail/CVE-2022-23950
- https://github.com/keylime/keylime/commit/ea5d0373fa2c050d5d95404eb779be7e8327b911
