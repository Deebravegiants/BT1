# [H] s390/pkey: Check length in pkey_pckmo handler implementation

## Summary
Severity: High
Advisory: CVE-2026-64558
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-64558
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/pkey: Check length in pkey_pckmo handler implementation

Explicitly check the length of the target buffer in the pkey_pckmo
implementation of the key_to_protkey() handler function. The handler
function fails, if the generated output data exceeds the length of the
provided target buffer.

## References
- https://git.kernel.org/stable/c/02028a24e26d85262ab9c8fc4344e1f3503007fc
- https://git.kernel.org/stable/c/1ac287e2af9a9112fe271427ef45eceb26bce8b4
- https://git.kernel.org/stable/c/433e5e70cdc1edf382d28d08a885b22e2b98b7da
- https://git.kernel.org/stable/c/614aa0491c7a190556c2345dddee0b6f5ed90989
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64558.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64558
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
