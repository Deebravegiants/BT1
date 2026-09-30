# [M] Kernel: memory leak via ksmbd session setup request with unknown ntlmssp message type

## Summary
Severity: Medium
Advisory: CVE-2023-32255
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-08-02
Source: https://osv.dev/vulnerability/CVE-2023-32255
Type: osv

## Details
A flaw was found in the Linux kernel's ksmbd component. A memory leak can occur if a client sends a session setup request with an unknown NTLMSSP message type,  potentially leading to resource exhaustion.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6d7cb549c2ca20e1f07593f15e936fd54b763028
- https://access.redhat.com/security/cve/CVE-2023-32255
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32255.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32255
- https://www.zerodayinitiative.com/advisories/ZDI-23-703/
- https://bugzilla.redhat.com/show_bug.cgi?id=2385884
