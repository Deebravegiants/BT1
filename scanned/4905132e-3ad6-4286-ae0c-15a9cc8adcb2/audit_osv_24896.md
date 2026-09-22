# [H] CVE-2023-28144

## Summary
Severity: High
Advisory: CVE-2023-28144
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2023-28144
Type: osv

## Details
KDAB Hotspot 1.3.x and 1.4.x through 1.4.1, in a non-default configuration, allows privilege escalation because of race conditions involving symlinks and elevate_perf_privileges.sh chown calls.

## References
- https://www.openwall.com/lists/oss-security/2023/03/14/8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28144.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28144
- https://github.com/KDAB/hotspot/releases
