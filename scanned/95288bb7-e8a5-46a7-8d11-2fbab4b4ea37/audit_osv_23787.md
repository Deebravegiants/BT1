# [M] mt76: mt7915: fix possible NULL pointer dereference in mt7915_mac_fill_rx_vector

## Summary
Severity: Medium
Advisory: CVE-2022-49484
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49484
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mt76: mt7915: fix possible NULL pointer dereference in mt7915_mac_fill_rx_vector

Fix possible NULL pointer dereference in mt7915_mac_fill_rx_vector
routine if the chip does not support dbdc and the hw reports band_idx
set to 1.

## References
- https://git.kernel.org/stable/c/268e8ef187eb8780d021b0e4f5ffa92dee5c4983
- https://git.kernel.org/stable/c/62fdc974894eec80d678523458cf99bbdb887e22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49484.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49484
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
