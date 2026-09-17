# [M] Gnome-remote-desktop: freerdp: unauthenticated rdp packet causes segfault in freerdp leading to denial of service

## Summary
Severity: Medium
Advisory: CVE-2025-4478
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-4478
Type: osv

## Details
A flaw was found in the FreeRDP used by Anaconda's remote install feature, where a crafted RDP packet could trigger a segmentation fault. This issue causes the service to crash and remain defunct, resulting in a denial of service. It occurs pre-boot and is likely due to a NULL pointer dereference. Rebooting is required to recover the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.freerdp.com/
- https://access.redhat.com/errata/RHSA-2025:9307
- https://access.redhat.com/security/cve/CVE-2025-4478
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4478.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4478
- https://bugzilla.redhat.com/show_bug.cgi?id=2365232
- https://github.com/FreeRDP/FreeRDP/pull/11573
