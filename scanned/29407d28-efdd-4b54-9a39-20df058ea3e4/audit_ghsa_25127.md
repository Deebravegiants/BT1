# [C] Juju uses a UNIX domain socket without setting appropriate permissions

## Summary
Severity: Critical
Advisory: GHSA-j3hp-pv6v-rgrx
CVE: CVE-2017-9232
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j3hp-pv6v-rgrx
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <0.0.0-20170524231039-0417178a3c28

## Details
Juju before 1.25.12, 2.0.x before 2.0.4, and 2.1.x before 2.1.3 uses a UNIX domain socket without setting appropriate permissions, allowing privilege escalation by users on the system to root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9232
- https://github.com/juju/juju/commit/0417178a3c2869537860e8b3b5e787ce1732231f
- https://bugs.launchpad.net/juju/+bug/1682411
- https://github.com/juju/juju
- https://www.exploit-db.com/exploits/44023
