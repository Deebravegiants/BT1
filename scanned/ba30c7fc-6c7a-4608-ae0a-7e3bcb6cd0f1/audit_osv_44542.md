# [M] Gvfs: sftp: uninitialized heap disclosure in read_string()

## Summary
Severity: Medium
Advisory: CVE-2026-84267
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84267
Type: osv

## Details
A flaw was found in the SFTP backend in gvfs. When mounting a share, a malicious SFTP server can cause read_string() to allocate a buffer with a certain length but the function does not verify that the buffer is completely filled, leaving the remainder of the buffer containing uninitialized heap contents. If the server sends a short FXP_HANDLE reply, these uninitialized bytes are taken as the file handle. The client will then echo these uninitialized bytes back to the server on all subsequent requests using that handle. With a length of 128 bytes, this issue allows the malicious server to deterministically read uninitialized heap memory from the gvfsd-sftp process, leaking its heap base and the load address of the libgio library, resulting in a deterministic defeat of Address Space Layout Randomization (ASLR).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-84267
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84267.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84267
- https://bugzilla.redhat.com/show_bug.cgi?id=2526466
- https://gitlab.gnome.org/GNOME/gvfs/-/issues/861
- https://gitlab.gnome.org/GNOME/gvfs
