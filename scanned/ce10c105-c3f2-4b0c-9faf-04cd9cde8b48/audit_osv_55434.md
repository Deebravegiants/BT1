# [M] CVE-2025-47712

## Summary
Severity: Medium
Advisory: CVE-2025-47712
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-47712
Type: osv

## Details
A flaw exists in the nbdkit "blocksize" filter that can be triggered by a specific type of client request. When a client requests block status information for a very large data range, exceeding a certain limit, it causes an internal error in the nbdkit, leading to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2025-47712
- https://lists.libguestfs.org/archives/list/guestfs@lists.libguestfs.org/thread/67E7AASHHADIY7VAD3FFW2I67LTWVWYF/
- https://bugzilla.redhat.com/show_bug.cgi?id=2365724
