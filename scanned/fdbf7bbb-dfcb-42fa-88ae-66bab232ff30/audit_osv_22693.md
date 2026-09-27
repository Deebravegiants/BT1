# [M] CVE-2022-3628

## Summary
Severity: Medium
Advisory: CVE-2022-3628
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-3628
Type: osv

## Details
A buffer overflow flaw was found in the Linux kernel Broadcom Full MAC Wi-Fi driver. This issue occurs when a user connects to a malicious USB device. This can allow a local user to crash the system or escalate their privileges.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/patch/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c?id=6788ba8aed4e28e90f72d68a9d794e34eac17295
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3628.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3628
