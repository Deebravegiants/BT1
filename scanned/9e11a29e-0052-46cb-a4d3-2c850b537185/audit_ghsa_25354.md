# [M] aptdaemon Information Disclosure via Improper Input Validation in Transaction class

## Summary
Severity: Medium
Advisory: GHSA-wpmr-q825-x4c6
CVE: CVE-2020-15703
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wpmr-q825-x4c6
Type: github-advisory

## Affected
- PyPI: `aptdaemon` — affected >=0 <1.1.1

## Details
There is no input validation on the Locale property in an apt transaction. An unprivileged user can supply a full path to a writable directory, which lets aptd read a file as root. Having a symlink in place results in an error message if the file exists, and no error otherwise. This way an unprivileged user can check for the existence of any files on the system as root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15703
- https://bugs.launchpad.net/ubuntu/+source/aptdaemon/+bug/1888235
- https://github.com/linuxmint/aptdaemon
- https://github.com/linuxmint/aptdaemon/blob/4d24cb61575ac6fbee8d5e61ef933e6093ee0a2e/debian/patches/CVE-2020-15703.patch
- https://ubuntu.com/security/notices/USN-4537-1
- https://www.eyecontrol.nl/blog/the-story-of-3-cves-in-ubuntu-desktop.html
