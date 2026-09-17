# [M] Flatpak metadata with ANSI control codes can cause misleading terminal output

## Summary
Severity: Medium
Advisory: CVE-2023-28101
Aliases: GHSA-h43h-fwqx-mpp8
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2023-03-16
Source: https://osv.dev/vulnerability/CVE-2023-28101
Type: osv

## Details
Flatpak is a system for building, distributing, and running sandboxed desktop applications on Linux. In versions prior to 1.10.8, 1.12.8, 1.14.4, and 1.15.4, if an attacker publishes a Flatpak app with elevated permissions, they can hide those permissions from users of the `flatpak(1)` command-line interface by setting other permissions to crafted values that contain non-printable control characters such as `ESC`. A fix is available in versions 1.10.8, 1.12.8, 1.14.4, and 1.15.4. As a workaround, use a GUI like GNOME Software rather than the command-line interface, or only install apps whose maintainers you trust.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28101.json
- https://github.com/flatpak/flatpak/security/advisories/GHSA-h43h-fwqx-mpp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-28101
- https://security.gentoo.org/glsa/202312-12
- https://github.com/flatpak/flatpak/commit/409e34187de2b2b2c4ef34c79f417be698830f6c
- https://github.com/flatpak/flatpak/commit/6cac99dafe6003c8a4bd5666341c217876536869
- https://github.com/flatpak/flatpak/commit/7fe63f2e8f1fd2dafc31d45154cf0b191ebec66c
