# [H] wifi: iwlwifi: mvm: don't set the MFP flag for the GTK

## Summary
Severity: High
Advisory: CVE-2024-27434
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27434
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: don't set the MFP flag for the GTK

The firmware doesn't need the MFP flag for the GTK, it can even make the
firmware crash. in case the AP is configured with: group cipher TKIP and
MFPC. We would send the GTK with cipher = TKIP and MFP which is of course
not possible.

## References
- https://git.kernel.org/stable/c/40405cbb20eb6541c603e7b3d54ade0a7be9d715
- https://git.kernel.org/stable/c/60f6d5fc84a9fd26528a24d8a267fc6a6698b628
- https://git.kernel.org/stable/c/b4f1b0b3b91762edd19bf9d3b2e4c3a0740501f8
- https://git.kernel.org/stable/c/e35f316bce9e5733c9826120c1838f4c447b2c4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27434.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
