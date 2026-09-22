# [H] smb3: missing lock when picking channel

## Summary
Severity: High
Advisory: CVE-2024-35999
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35999
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.91, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb3: missing lock when picking channel

Coverity spotted a place where we should have been holding the
channel lock when accessing the ses channel index.

Addresses-Coverity: 1582039 ("Data race condition (MISSING_LOCK)")

## References
- https://git.kernel.org/stable/c/0fcf7e219448e937681216353c9a58abae6d3c2e
- https://git.kernel.org/stable/c/60ab245292280905603bc0d3654f4cf8fceccb00
- https://git.kernel.org/stable/c/8094a600245e9b28eb36a13036f202ad67c1f887
- https://git.kernel.org/stable/c/98c7ed29cd754ae7475dc7cb3f33399fda902729
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35999.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
