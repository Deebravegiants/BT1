# [M] Xorg-x11-server-xwayland: xorg-x11-server: tigervnc: data leak in xfixes extension's xfixessetclientdisconnectmode

## Summary
Severity: Medium
Advisory: CVE-2025-49177
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-49177
Type: osv

## Details
A flaw was found in the XFIXES extension. The XFixesSetClientDisconnectMode handler does not validate the request length, allowing a client to read unintended memory from previous requests.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.x.org/wiki/Development/Security/
- https://access.redhat.com/errata/RHSA-2025:10258
- https://access.redhat.com/errata/RHSA-2025:9303
- https://access.redhat.com/errata/RHSA-2025:9304
- https://access.redhat.com/security/cve/CVE-2025-49177
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49177.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49177
- https://bugzilla.redhat.com/show_bug.cgi?id=2369955
- https://gitlab.freedesktop.org/xorg/xserver/-/commit/ab02fb96b1c701c3bb47617d965522c34befa6af
- https://gitlab.freedesktop.org/xorg/xserver
