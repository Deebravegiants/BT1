# [M] x86/MCE/AMD: Fix memory leak when threshold_create_bank() fails

## Summary
Severity: Medium
Advisory: CVE-2022-49549
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49549
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/MCE/AMD: Fix memory leak when threshold_create_bank() fails

In mce_threshold_create_device(), if threshold_create_bank() fails, the
previously allocated threshold banks array @bp will be leaked because
the call to mce_threshold_remove_device() will not free it.

This happens because mce_threshold_remove_device() fetches the pointer
through the threshold_banks per-CPU variable but bp is written there
only after the bank creation is successful, and not before, when
threshold_create_bank() fails.

Add a helper which unwinds all the bank creation work previously done
and pass into it the previously allocated threshold banks array for
freeing.

  [ bp: Massage. ]

## References
- https://git.kernel.org/stable/c/396b8e7ab2a99ddac57d3522b3da5e58cb608d37
- https://git.kernel.org/stable/c/9708f1956eeb70c86943e0bc62fa3b0101b59616
- https://git.kernel.org/stable/c/b4acb8e7f1594607bc9017ef0aacb40b24a003d6
- https://git.kernel.org/stable/c/cc0dd4456f9573bf8af9b4d8754433918e809e1e
- https://git.kernel.org/stable/c/e5f28623ceb103e13fc3d7bd45edf9818b227fd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49549.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49549
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
