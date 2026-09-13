# [H] KEYS: trusted: dcp: fix NULL dereference in AEAD crypto operation

## Summary
Severity: High
Advisory: CVE-2024-50281
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50281
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KEYS: trusted: dcp: fix NULL dereference in AEAD crypto operation

When sealing or unsealing a key blob we currently do not wait for
the AEAD cipher operation to finish and simply return after submitting
the request. If there is some load on the system we can exit before
the cipher operation is done and the buffer we read from/write to
is already removed from the stack. This will e.g. result in NULL
pointer dereference errors in the DCP driver during blob creation.

Fix this by waiting for the AEAD cipher operation to finish before
resuming the seal and unseal calls.

## References
- https://git.kernel.org/stable/c/04de7589e0a95167d803ecadd115235ba2c14997
- https://git.kernel.org/stable/c/c75e0272289eae18c5379518a9c56ef31d65cc7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50281.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50281
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
