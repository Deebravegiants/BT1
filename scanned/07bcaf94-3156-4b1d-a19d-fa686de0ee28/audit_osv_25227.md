# [H] Kernel: ksmbd race issue from smb2 close and logoff with multichannel

## Summary
Severity: High
Advisory: CVE-2023-32256
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2023-32256
Type: osv

## Details
A flaw was found in the Linux kernel's ksmbd component. A race condition between smb2 close operation and logoff in multichannel connections could result in a use-after-free issue.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=abcc506a9a71976a8b4c9bf3ee6efd13229c1e19
- https://access.redhat.com/security/cve/CVE-2023-32256
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32256.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-32256
- https://www.zerodayinitiative.com/advisories/ZDI-23-704/
- https://bugzilla.redhat.com/show_bug.cgi?id=2385885
