# [H] Libsoup: heap use-after-free in libsoup message queue handling during http/2 read completion

## Summary
Severity: High
Advisory: CVE-2025-12105
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-23
Source: https://osv.dev/vulnerability/CVE-2025-12105
Type: osv

## Details
A flaw was found in the asynchronous message queue handling of the libsoup library, widely used by GNOME and WebKit-based applications to manage HTTP/2 communications. When network operations are aborted at specific timing intervals, an internal message queue item may be freed twice due to missing state synchronization. This leads to a use-after-free memory access, potentially crashing the affected application. Attackers could exploit this behavior remotely by triggering specific HTTP/2 read and cancel sequences, resulting in a denial-of-service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:23139
- https://access.redhat.com/errata/RHSA-2025:23437
- https://access.redhat.com/security/cve/CVE-2025-12105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12105.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-12105
- https://bugzilla.redhat.com/show_bug.cgi?id=2405992
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/481
- https://gitlab.gnome.org/GNOME/libsoup
