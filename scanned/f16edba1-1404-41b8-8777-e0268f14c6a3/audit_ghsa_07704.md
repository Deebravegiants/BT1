# [M] Moodle has an authorization logic flaw

## Summary
Severity: Medium
Advisory: GHSA-hcm6-q6pc-xfhm
CVE: CVE-2025-67856
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-hcm6-q6pc-xfhm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.1.22
- Packagist: `moodle/moodle` — affected >=4.4.0-beta <4.4.12
- Packagist: `moodle/moodle` — affected >=4.5.0-beta <4.5.8
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.4
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.1

## Details
A flaw was found in Moodle. An authorization logic flaw, specifically due to incomplete role checks during the badge awarding process, allowed badges to be granted without proper verification. This could enable unauthorized users to obtain badges they are not entitled to, potentially leading to privilege escalation or unauthorized access to certain features.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67856
- https://github.com/moodle/moodle/commit/0d48779e61bcacbabbcb82858a037b567351fce0
- https://access.redhat.com/security/cve/CVE-2025-67856
- https://bugzilla.redhat.com/show_bug.cgi?id=2423864
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=471306
