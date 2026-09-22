# [M] Tuned: improper sanitization of `instance_name` parameter of the `instance_create()` method

## Summary
Severity: Medium
Advisory: CVE-2024-52337
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-52337
Type: osv

## Details
A log spoofing flaw was found in the Tuned package due to improper sanitization of some API arguments. This flaw allows an attacker to pass a controlled sequence of characters; newlines can be inserted into the log. Instead of the 'evil' the attacker could mimic a valid TuneD log line and trick the administrator. The quotes '' are usually used in TuneD logs citing raw user input, so there will always be the ' character ending the spoofed input, and the administrator can easily overlook this. This logged string is later used in logging and in the output of utilities, for example, `tuned-adm get_instances` or other third-party programs that use Tuned's D-Bus interface for such operations.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/redhat-performance/tuned/releases/tag/v2.24.1
- https://security.opensuse.org/2024/11/26/tuned-instance-create.html
- https://www.openwall.com/lists/oss-security/2024/11/28/1
- https://www.openwall.com/lists/oss-security/2024/11/28/2
- https://access.redhat.com/errata/RHSA-2024:10381
- https://access.redhat.com/errata/RHSA-2024:10384
- https://access.redhat.com/errata/RHSA-2024:11161
- https://access.redhat.com/errata/RHSA-2025:0195
- https://access.redhat.com/errata/RHSA-2025:0327
- https://access.redhat.com/errata/RHSA-2025:0368
- https://access.redhat.com/errata/RHSA-2025:0879
- https://access.redhat.com/errata/RHSA-2025:0880
- https://access.redhat.com/errata/RHSA-2025:0881
- https://access.redhat.com/errata/RHSA-2025:1785
- https://access.redhat.com/errata/RHSA-2025:1802
- https://access.redhat.com/security/cve/CVE-2024-52337
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52337.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52337
- https://bugzilla.redhat.com/show_bug.cgi?id=2324541
