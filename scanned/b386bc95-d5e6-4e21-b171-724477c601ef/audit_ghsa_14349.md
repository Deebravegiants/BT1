# [M] alextselegidis/easyappointments Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4qmm-cv4r-qfr4
CVE: CVE-2023-2105
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-15
Source: https://github.com/advisories/GHSA-4qmm-cv4r-qfr4
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0

## Details
alextselegidis/easyappointments is vulnerable to session fixation. The application does not generate a new `ea_session` cookie after the user authenticates. A malicious user may create a new session cookie value and inject it to a victim. After the victim logs in, the injected cookie becomes valid, giving the attacker access to the user's account through the active session. If an attacker conducts this attack against an admin user, the attacker may escalate their privileges with the admin user being unaware.

This issue is patched in commit 7f37350fab9d729a9350d96369ff0f453cf7b840 and anticipated to be part of version 1.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2105
- https://github.com/alextselegidis/easyappointments/commit/7f37350fab9d729a9350d96369ff0f453cf7b840
- https://github.com/alextselegidis/easyappointments
- https://huntr.dev/bounties/de213e0b-a227-4fc3-bbe7-0b33fbf308e1
