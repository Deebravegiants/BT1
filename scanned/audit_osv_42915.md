# [H] platform/x86: dell-laptop: fix missing cleanups in init error path

## Summary
Severity: High
Advisory: CVE-2026-72144
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72144
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <6.6.148, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: dell-laptop: fix missing cleanups in init error path

dell_init() initializes several resources after dell_setup_rfkill(),
including the optional touchpad LED, keyboard backlight LED, battery
hook, debugfs directory and dell-laptop notifier.

If a later LED or backlight registration fails, the error path only
tears down the battery hook and rfkill resources. This leaves the
notifier, debugfs directory, keyboard backlight LED and optional
touchpad LED registered after dell_init() returns an error.

Add the missing cleanup calls before tearing down rfkill.

## References
- https://git.kernel.org/stable/c/1e41ca4a7fba2e680d6950e9511245255fffa46c
- https://git.kernel.org/stable/c/6bd76d5421a72d2526c9be8f01f55bee960f899f
- https://git.kernel.org/stable/c/6e9cab2247e5b243ae2d907ce7c948a8a9c8d61a
- https://git.kernel.org/stable/c/b351e082711d12f075a36a6cd67709693689315f
- https://git.kernel.org/stable/c/e4908b3bed755f73870416b971e162a8d0ef0aef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72144.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72144
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
