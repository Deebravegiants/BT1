# [H] Local Privilege Escalation in Windows

## Summary
Severity: High
Advisory: GHSA-9w2p-rh8c-v9g5
CVE: CVE-2023-49797
CWE: CWE-379, CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-09
Source: https://github.com/advisories/GHSA-9w2p-rh8c-v9g5
Type: github-advisory

## Affected
- PyPI: `pyinstaller` — affected >=0 <5.13.1

## Details
### Impact

A PyInstaller built application, elevated as a privileged process, may be tricked by an unprivileged attacker into deleting files the unprivileged user does not otherwise have access to.

A user is affected if **all** the following are satisfied:

* The user runs an application containing either `matplotlib` or `win32com`.
* The application is ran as administrator (or at least a user with higher privileges than the attacker).
* The user's temporary directory is not locked to that specific user (most likely due to `TMP`/`TEMP` environment variables pointing to an unprotected, arbitrary, non default location).
* Either:
  - The attacker is able to very carefully time the replacement of a temporary file with a symlink. This switch must occur exactly between [`shutil.rmtree()`'s builtin symlink check](https://github.com/python/cpython/blob/0fb18b02c8ad56299d6a2910be0bab8ad601ef24/Lib/shutil.py#L623) and the deletion itself
  - The application was built with Python 3.7.x or earlier which has no protection against Directory Junctions links

### Patches

The vulnerability has been addressed in https://github.com/pyinstaller/pyinstaller/pull/7827 which corresponds to `pyinstaller >= 5.13.1`

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No workaround, although the attack complexity becomes much higher if the application is built with Python >= 3.8.0.

## References
- https://github.com/pyinstaller/pyinstaller/security/advisories/GHSA-9w2p-rh8c-v9g5
- https://nvd.nist.gov/vuln/detail/CVE-2023-49797
- https://github.com/pyinstaller/pyinstaller/pull/7827
- https://github.com/pyinstaller/pyinstaller
- https://github.com/pypa/advisory-database/tree/main/vulns/pyinstaller/PYSEC-2023-292.yaml
- https://github.com/python/cpython/blob/0fb18b02c8ad56299d6a2910be0bab8ad601ef24/Lib/shutil.py#L623
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2K2XIQLEMZIKUQUOWNDYWTEWYQTKMAN7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ISRWT34FAF23PUOLVZ7RVWBZMWPDR5U7
