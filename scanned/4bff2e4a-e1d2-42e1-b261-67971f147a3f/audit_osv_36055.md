# [C] Jenkins - FilePath.untarFrom() Symlink Target Validation Bypass and Blank-Name Check Bypass (Arbitrary File Read)

## Summary
Severity: Critical
Advisory: CVE-2026-19429
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-19429
Type: osv

## Details
Jenkins FilePath.untarFrom() does not validate symlink targets in extracted TAR archives, even in versions patched for CVE-2026-33001 and CVE-2026-70427. An authenticated attacker with job configuration privileges can include a malicious archive in a build step that creates workspace symlinks pointing to arbitrary files on the Jenkins controller. By reading the secrets directory, the attacker obtains the cryptographic keys used to sign remember-me cookies, forges a valid administrator session cookie without any admin interaction, and gains access to the Script Console for remote code execution. Jenkins 2.576 is additionally affected by a bypass of the CVE-2026-70427 blank-name check via Unicode zero-width characters (U+200B, U+200C, U+200D, U+2060, U+00AD), which Java's String.isBlank() does not recognize as whitespace.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19429.json
- https://github.com/jenkinsci/jenkins
- https://nvd.nist.gov/vuln/detail/CVE-2026-19429
- https://www.jenkins.io/security/advisory/2026-03-18/#SECURITY-3657
- https://www.jenkins.io/security/advisory/2026-08-05/
