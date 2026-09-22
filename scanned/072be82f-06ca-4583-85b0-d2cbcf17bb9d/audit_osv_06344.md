# [M] CPython >3.11 Insecure Input Validation resulting in privilege escalation

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-12003
Aliases: BIT-python-2026-12003, BIT-python-min-2026-12003, CVE-2026-12003, PSF-2026-28
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-libpython-2026-12003
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.7

## Details
To allow builds of Python to be run from an in-tree layout (rather than
an installed file layout), the VPATH variable is defined at build time
and used to locate certain landmarks - specifically,
Modules/setup.local. When this landmark is found relative to VPATH
relative to the executable, Python assumes it is running in a source
tree and generates a different default sys.path. This code remains in
release builds, so that release-ready builds can be built in-tree.

On Windows, since builds are written to 'PCbuild/', the value of
VPATH is set to '..\..', which results in a landmark of
'..\..\Modules\setup.local'. This path is outside the install directory
of Python, and may have different permissions, potentially allowing a
low-privilege user to create the landmark and an alternative `Lib`
folder that will be discovered by an otherwise restricted install.

Such a setup occurs with the legacy default install location for all
users (in the now superseded EXE installer), due to how Windows allows
all users to create folders in the root directory of their OS drive.

Our recommended mitigation on Windows is to migrate away from the
legacy installer and use the new [Python install
manager](https://www.python.org/downloads/latest/pymanager/) to install
for the current user. Installs where the directory two levels above the
Python installation directory have equivalent permissions are unaffected
(in general, a per-user install cannot be modified at all by other
users, removing any escalation of privilege risk, and could be directly
modified by a privileged user, making the potential tampering
irrelevant). Alternative mitigations might include preemptively creating
and restricting access to a `Modules` directory. Be aware that only 3.13
and 3.14 will receive updated legacy installers - earlier fixes are only
provided as sources.

Platforms other than Windows allow VPATH to be overridden, but as they
don't usually use a separated directory in the build for binaries, are
unlikely to have a landmark reference outside of the install directory.

The landmark detection involving VPATH is a fallback for when a more
specific landmark - .\pybuilddir.txt - is absent, and was included for
compatibility. Future releases of Python will no longer include the
fallback, and so builds will need to generate or preserve the
pybuilddir.txt file in order to work in-tree. This landmark file has
been generated on Windows since 3.11, and on other platforms for longer.

## References
- http://www.openwall.com/lists/oss-security/2026/06/16/8
- https://github.com/python/cpython/commit/16c40f944b7bff724a403cf4902763d095bb4b2a
- https://github.com/python/cpython/commit/9e863fab283eddca9c2a8f9d1ee30f4dc243e314
- https://github.com/python/cpython/commit/a86de0bc236fbb9452f98998fc8437e9fca35700
- https://github.com/python/cpython/commit/b93d6d3399adbd3a5037b6b92fc3587c85ac5d56
- https://github.com/python/cpython/issues/151544
- https://github.com/python/cpython/pull/151545
- https://https://mail.python.org/archives/list/security-announce@python.org/thread/JIFOBO7UX3LY4VJKJUOKYJV62CFR2IRH/
- https://nvd.nist.gov/vuln/detail/CVE-2026-12003
- https://github.com/python/cpython/commit/03ab7b44788bfd6b8927e16bcdbd025aa08dce06
- https://github.com/python/cpython/commit/872038377db2e170e0e140b5f8aaedf636b3fbf5
