# [M] ALPINE-CVE-2021-28694

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28694
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28694
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=0 <4.13.3-r2
- Alpine:v3.12: `xen` — affected >=0 <4.13.3-r2
- Alpine:v3.13: `xen` — affected >=0 <4.14.2-r0
- Alpine:v3.14: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.15: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.16: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.17: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.18: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.19: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.20: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.21: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.22: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.23: `xen` — affected >=0 <4.15.0-r2
- Alpine:v3.24: `xen` — affected >=0 <4.15.0-r2

## Details
IOMMU page mapping issues on x86 T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Both AMD and Intel allow ACPI tables to specify regions of memory which should be left untranslated, which typically means these addresses should pass the translation phase unaltered. While these are typically device specific ACPI properties, they can also be specified to apply to a range of devices, or even all devices. On all systems with such regions Xen failed to prevent guests from undoing/replacing such mappings (CVE-2021-28694). On AMD systems, where a discontinuous range is specified by firmware, the supposedly-excluded middle range will also be identity-mapped (CVE-2021-28695). Further, on AMD systems, upon de-assigment of a physical device from a guest, the identity mappings would be left in place, allowing a guest continued access to ranges of memory which it shouldn't have access to anymore (CVE-2021-28696).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28694
