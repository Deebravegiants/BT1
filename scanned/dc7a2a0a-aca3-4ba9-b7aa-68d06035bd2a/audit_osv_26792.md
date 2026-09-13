# [C] x86/sev: Make enc_dec_hypercall() accept a size instead of npages

## Summary
Severity: Critical
Advisory: CVE-2023-53996
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-53996
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/sev: Make enc_dec_hypercall() accept a size instead of npages

enc_dec_hypercall() accepted a page count instead of a size, which
forced its callers to round up. As a result, non-page aligned
vaddrs caused pages to be spuriously marked as decrypted via the
encryption status hypercall, which in turn caused consistent
corruption of pages during live migration. Live migration requires
accurate encryption status information to avoid migrating pages
from the wrong perspective.

## References
- https://git.kernel.org/stable/c/6615212d8e131b45bd9705b0d69cc0d2f624666f
- https://git.kernel.org/stable/c/8ae7457e71a320867d868f2622d7c643596e4f43
- https://git.kernel.org/stable/c/ac3f9c9f1b37edaa7d1a9b908bc79d843955a1a2
- https://git.kernel.org/stable/c/ba50e7773a99a109a1ea6f753b766a080d3b21cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53996.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53996
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
