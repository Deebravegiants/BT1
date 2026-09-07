# [H] ClusterLabs crmsh vulnerable to shell code injection

## Summary
Severity: High
Advisory: GHSA-99xx-83jm-h24m
CVE: CVE-2020-35459
CWE: CWE-269, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-99xx-83jm-h24m
Type: github-advisory

## Affected
- PyPI: `crmsh` — affected >=0

## Details
An issue was discovered in ClusterLabs crmsh through 4.2.1. Local attackers able to call `crm history` (when `crm` is run) were able to execute commands via shell code injection to the crm history commandline, potentially allowing escalation of privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35459
- https://bugzilla.suse.com/show_bug.cgi?id=1179999
- https://github.com/ClusterLabs/crmsh
- https://github.com/ClusterLabs/crmsh/blob/a403aa15f3ea575adfe5e43bf2a31c9f9094fcda/crmsh/history.py#L476
- https://github.com/ClusterLabs/crmsh/releases
- https://lists.debian.org/debian-lts-announce/2021/01/msg00021.html
- https://www.openwall.com/lists/oss-security/2021/01/12/3
- http://www.openwall.com/lists/oss-security/2021/01/12/3
