# [H] ice: fix NULL access of tx->in_use in ice_ll_ts_intr

## Summary
Severity: High
Advisory: CVE-2025-39854
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39854
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix NULL access of tx->in_use in ice_ll_ts_intr

Recent versions of the E810 firmware have support for an extra interrupt to
handle report of the "low latency" Tx timestamps coming from the
specialized low latency firmware interface. Instead of polling the
registers, software can wait until the low latency interrupt is fired.

This logic makes use of the Tx timestamp tracking structure, ice_ptp_tx, as
it uses the same "ready" bitmap to track which Tx timestamps complete.

Unfortunately, the ice_ll_ts_intr() function does not check if the
tracker is initialized before its first access. This results in NULL
dereference or use-after-free bugs similar to the issues fixed in the
ice_ptp_ts_irq() function.

Fix this by only checking the in_use bitmap (and other fields) if the
tracker is marked as initialized. The reset flow will clear the init field
under lock before it tears the tracker down, thus preventing any
use-after-free or NULL access.

## References
- https://git.kernel.org/stable/c/2cde98a02da958357fe240a6ba269b69d913b6ba
- https://git.kernel.org/stable/c/923c267bdbb64f65bc1149d184efcf8b047d7d64
- https://git.kernel.org/stable/c/f6486338fde3f04ed0ec59fe67a69a208c32734f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39854.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39854
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
