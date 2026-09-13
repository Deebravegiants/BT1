# [C] PDF /GoToR action argv injection enables single-click RCE via --gtk-module dlopen

## Summary
Severity: Critical
Advisory: CVE-2026-46529
Aliases: GHSA-vgv2-m826-8f6f
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46529
Type: osv

## Details
Atril Document Viewer is the default document reader of the MATE desktop environment for Linux. A single-click remote code execution vulnerability in versions prior to 1.26.3 and 1.28.4 allows an attacker to achieve arbitrary code execution as the user by tricking them into clicking a link inside a malicious PDF document. The PDF can be packaged as a polyglot file that is simultaneously a valid PDF and a valid ELF shared library, making the attack a single-file, single-click, configuration-independent RCE on stock atril installations. The root cause is `shell/ev-application.c:ev_spawn`, which builds a command line from attacker-controlled PDF link-destination fields without applying `g_shell_quote`. The cmdline is then handed to `g_app_info_create_from_commandline`, which shell-parses it back into argv — splitting any embedded `--gtk-module=PATH` into a separate argv element. GTK then `dlopen()`s the path during init, running any `__attribute__((constructor))` it finds. Versions 1.26.3 and 1.28.4 contain a patch for the issue. This is the same defect class as CVE-2023-51698 (CBT `--checkpoint-action` injection in `comics-document.c`, fixed in 1.6.2) but in a different code path (`shell/ev-application.c`) that the original patch did not touch.

## References
- http://www.openwall.com/lists/oss-security/2026/05/19/34
- http://www.openwall.com/lists/oss-security/2026/05/21/7
- http://www.openwall.com/lists/oss-security/2026/05/22/11
- https://github.com/mate-desktop/atril/releases/tag/v1.26.3
- https://github.com/mate-desktop/atril/releases/tag/v1.28.4
- https://lists.debian.org/debian-lts-announce/2026/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2026/05/msg00042.html
- https://lists.debian.org/debian-lts-announce/2026/06/msg00021.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46529.json
- https://access.redhat.com/errata/RHSA-2026:27819
- https://access.redhat.com/errata/RHSA-2026:28998
- https://access.redhat.com/errata/RHSA-2026:33169
- https://access.redhat.com/errata/RHSA-2026:33416
- https://access.redhat.com/errata/RHSA-2026:39115
- https://access.redhat.com/errata/RHSA-2026:41904
- https://access.redhat.com/errata/RHSA-2026:42692
- https://access.redhat.com/errata/RHSA-2026:43398
- https://access.redhat.com/errata/RHSA-2026:46467
- https://access.redhat.com/security/cve/CVE-2026-46529
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46529.json
