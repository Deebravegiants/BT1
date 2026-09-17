# [H] Pipewire: pipewire: sandbox escape and arbitrary code execution via malicious library loading

## Summary
Severity: High
Advisory: CVE-2026-5674
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-5674
Type: osv

## Details
A flaw was found in PipeWire, a multimedia server. This vulnerability allows an attacker to escape sandboxed applications, such as Flatpak, by exploiting PipeWire's PulseAudio compatibility layer. An attacker with minimal permissions within a sandboxed environment can load a malicious library, leading to arbitrary code execution outside the sandbox and potential compromise of the user's system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:47082
- https://access.redhat.com/errata/RHSA-2026:47083
- https://access.redhat.com/errata/RHSA-2026:51064
- https://access.redhat.com/errata/RHSA-2026:56028
- https://access.redhat.com/errata/RHSA-2026:56029
- https://access.redhat.com/errata/RHSA-2026:61768
- https://access.redhat.com/security/cve/CVE-2026-5674
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5674.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5674
- https://bugzilla.redhat.com/show_bug.cgi?id=2455341
- https://gitlab.freedesktop.org/pipewire/pipewire
