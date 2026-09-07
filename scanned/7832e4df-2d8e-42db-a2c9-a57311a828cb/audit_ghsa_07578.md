# [H] Moodle has a Remote Code Execution risk via file restore

## Summary
Severity: High
Advisory: GHSA-ggxq-2mg9-8966
CVE: CVE-2026-26045
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-21
Source: https://github.com/advisories/GHSA-ggxq-2mg9-8966
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.2
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.5
- Packagist: `moodle/moodle` — affected >=0 <4.5.9

## Details
A flaw was identified in Moodle’s backup restore functionality where specially crafted backup files were not properly validated during processing. If a malicious backup file is restored, it could lead to unintended execution of server-side code. Since restore capabilities are typically available to privileged users, exploitation requires authenticated access. Successful exploitation could result in full compromise of the Moodle server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26045
- https://github.com/moodle/moodle/commit/566054ba11f609a6d48d09b32e85d435d49927da
- https://access.redhat.com/security/cve/CVE-2026-26045
- https://bugzilla.redhat.com/show_bug.cgi?id=2440901
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=473314
