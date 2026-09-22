# [H] Local Privilege Escalation in PyInstaller

## Summary
Severity: High
Advisory: GHSA-7fcj-pq9j-wh2r
CVE: CVE-2019-16784
CWE: CWE-250
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-16
Source: https://github.com/advisories/GHSA-7fcj-pq9j-wh2r
Type: github-advisory

## Affected
- PyPI: `PyInstaller` — affected >=0 <3.6

## Details
### Impact

Local Privilege Escalation in all Windows software frozen by PyInstaller in "onefile" mode.

The vulnerability is present only on Windows and in this particular case: If a **software frozen by PyInstaller in "onefile" mode** is launched by a (privileged) user who has **his/her "TempPath" resolving to a world writable directory**. This is the case e.g. if the software is launched as a service or as a scheduled task using a system account (in which case TempPath will default to C:\Windows\Temp).

In order to be exploitable the software has to be (re)started after the attacker has launched the exploit program. So for a service launched at startup, a service restart is needed (e.g. after a crash or an upgrade).

While PyInstaller itself was not vulnerable, all Windows software frozen by PyInstaller in "onefile" mode is vulnerable.

CVSSv3 score 7.0 (High)
CVSSv3 vector CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H

Affected
- all Windows software frozen by PyInstaller in "onefile" mode

No affected
- PyInstaller itself (except if frozen by PyInstaller in "onefile" mode on Windows)
- software frozen in "one*dir*" mode
- other platforms (GNU/Linux, OS X, BSD, etc.)

### Patches
The problem is patched in commits 42a67148b3bdf9211fda8499fdc5b63acdd7e6cc (fixed code) and be948cf0954707671aa499da17b10c86b6fa5e5c (recompiled bootloaders). Users should upgrade to PyInstaller version 3.6 and rebuild their software.

### Workarounds
There is no known workaround. Users using PyInstaller to freeze their Windows software using "onefile" mode should upgrade PyInstaller and rebuild their software.

### Credits
This vulnerability was discovered and reported by Farid AYOUJIL (@faridtsl), David HA, Florent LE NIGER and Yann GASCUEL (@lnv42) from Alter Solutions (@AlterSolutions) and fixed in collaboration with
Hartmut Goebel (@htgoebel, maintainer of PyInstaller).

### Funding Development

PyInstaller is in urgent need of funding to make future security fixes happen, see <https://github.com/pyinstaller/pyinstaller/issues/4404> for details.

## References
- https://github.com/pyinstaller/pyinstaller/security/advisories/GHSA-7fcj-pq9j-wh2r
- https://nvd.nist.gov/vuln/detail/CVE-2019-16784
- https://github.com/pyinstaller/pyinstaller/commit/42a67148b3bdf9211fda8499fdc5b63acdd7e6cc
- https://github.com/pyinstaller/pyinstaller/commit/be948cf0954707671aa499da17b10c86b6fa5e5c
- https://github.com/pyinstaller/pyinstaller
- https://github.com/pypa/advisory-database/tree/main/vulns/pyinstaller/PYSEC-2020-175.yaml
