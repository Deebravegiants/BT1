# [H] Incorrect Permission Assignment for Critical Resource in Singularity

## Summary
Severity: High
Advisory: GHSA-557g-r22w-9wvx
CVE: CVE-2019-11328
CWE: CWE-269, CWE-732
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-557g-r22w-9wvx
Type: github-advisory

## Affected
- Go: `github.com/sylabs/singularity` — affected >=3.1.0 <3.2.0

## Details
An issue was discovered in Singularity 3.1.0 to 3.2.0-rc2, a malicious user with local/network access to the host system (e.g. ssh) could exploit this vulnerability due to insecure permissions allowing a user to edit files within `/run/singularity/instances/sing/<user>/<instance>`. The manipulation of those files can change the behavior of the starter-suid program when instances are joined resulting in potential privilege escalation on the host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11328
- https://github.com/sylabs/singularity/commit/618c9d56802399adb329c23ea2b70598eaff4a31
- https://github.com/sylabs/singularity/releases/tag/v3.2.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5O3TPL5OOTIZEI4H6IQBCCISBARJ6WL3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LIHV7DSEVTB5SUPEZ2UXGS3Q6WMEQSO2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LNU5BUHFOTYUZVHFUSX2VG4S3RCPUEMA
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00059.html
- http://www.openwall.com/lists/oss-security/2019/05/16/1
- http://www.securityfocus.com/bid/108360
