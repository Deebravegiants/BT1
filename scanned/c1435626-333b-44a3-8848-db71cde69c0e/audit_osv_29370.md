# [H] Bluetooth: Ignore too large handle values in BIG

## Summary
Severity: High
Advisory: CVE-2024-42133
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42133
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Ignore too large handle values in BIG

hci_le_big_sync_established_evt is necessary to filter out cases where the
handle value is belonging to ida id range, otherwise ida will be erroneously
released in hci_conn_cleanup.

## References
- https://git.kernel.org/stable/c/015d79c96d62cd8a4a359fcf5be40d58088c936b
- https://git.kernel.org/stable/c/38263088b845abeeeb98dda5b87c0de3063b6dbb
- https://git.kernel.org/stable/c/a06a8cc80fa203fde828a8429583f7e4fe27eca4
- https://git.kernel.org/stable/c/dad0003ccc68457baf005a6ed75b4d321463fe3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42133.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
