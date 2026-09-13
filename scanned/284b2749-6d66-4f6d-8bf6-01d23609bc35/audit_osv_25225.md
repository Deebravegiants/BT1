# [M] Kernel: deadlock in ksmbd_find_crypto_ctx()

## Summary
Severity: Medium
Advisory: CVE-2023-32253
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-02
Source: https://osv.dev/vulnerability/CVE-2023-32253
Type: osv

## Details
A flaw was found in the Linux kernel's ksmbd component. A deadlock is triggered by sending multiple concurrent session setup requests, possibly leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/
- https://access.redhat.com/security/cve/CVE-2023-32253
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32253.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32253
- https://bugzilla.redhat.com/show_bug.cgi?id=2385886
