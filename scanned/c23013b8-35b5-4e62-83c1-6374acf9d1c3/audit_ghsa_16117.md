# [H] Moodle Remote Code Execution vulnerability

## Summary
Severity: High
Advisory: GHSA-v6f4-v8h8-3c87
CVE: CVE-2024-43425
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-v6f4-v8h8-3c87
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.12
- Packagist: `moodle/moodle` — affected >=4.2.0-beta <4.2.9
- Packagist: `moodle/moodle` — affected >=4.3.0-beta <4.3.6
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.2

## Details
A flaw was found in Moodle. Additional restrictions are required to avoid a remote code execution risk in calculated question types. Note: This requires the capability to add/update questions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43425
- https://bugzilla.redhat.com/show_bug.cgi?id=2304253
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=461193
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-82576
