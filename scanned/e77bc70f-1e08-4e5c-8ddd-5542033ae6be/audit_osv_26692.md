# [H] wifi: iwlwifi: mvm: don't trust firmware n_channels

## Summary
Severity: High
Advisory: CVE-2023-53589
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53589
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: don't trust firmware n_channels

If the firmware sends us a corrupted MCC response with
n_channels much larger than the command response can be,
we might copy far too much (uninitialized) memory and
even crash if the n_channels is large enough to make it
run out of the one page allocated for the FW response.

Fix that by checking the lengths. Doing a < comparison
would be sufficient, but the firmware should be doing
it correctly, so check more strictly.

## References
- https://git.kernel.org/stable/c/05ad5a4d421ce65652fcb24d46b7e273130240d6
- https://git.kernel.org/stable/c/557ba100d8cf3661ff8d71c0b4a2cba8db555ec2
- https://git.kernel.org/stable/c/682b6dc29d98e857e6ca4bbc077c7dc2899b7473
- https://git.kernel.org/stable/c/c176f03350954b795322de0bfe1d7b514db41f45
- https://git.kernel.org/stable/c/d0d39bed9e95f27a246be91c5929254ac043ed30
- https://git.kernel.org/stable/c/e519a404a5bbba37693cb10fa61794a5fce4fd9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53589.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
