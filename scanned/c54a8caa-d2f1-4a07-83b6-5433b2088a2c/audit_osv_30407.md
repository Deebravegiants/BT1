# [H] Tuned: `script_pre` and `script_post` options allow to pass arbitrary scripts executed by root

## Summary
Severity: High
Advisory: CVE-2024-52336
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-52336
Type: osv

## Details
A script injection vulnerability was identified in the Tuned package. The `instance_create()` D-Bus function can be called by locally logged-in users without authentication. This flaw allows a local non-privileged user to execute a D-Bus call with `script_pre` or `script_post` options that permit arbitrary scripts with their absolute paths to be passed. These user or attacker-controlled executable scripts or programs could then be executed by Tuned with root privileges that could allow attackers to local privilege escalation.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/redhat-performance/tuned/releases/tag/v2.24.1
- https://security.opensuse.org/2024/11/26/tuned-instance-create.html
- https://www.openwall.com/lists/oss-security/2024/11/28/1
- https://www.openwall.com/lists/oss-security/2024/11/28/2
- https://access.redhat.com/errata/RHSA-2024:10384
- https://access.redhat.com/errata/RHSA-2025:0879
- https://access.redhat.com/errata/RHSA-2025:0880
- https://access.redhat.com/security/cve/CVE-2024-52336
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52336.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52336
- https://bugzilla.redhat.com/show_bug.cgi?id=2324540
- https://github.com/redhat-performance/tuned
