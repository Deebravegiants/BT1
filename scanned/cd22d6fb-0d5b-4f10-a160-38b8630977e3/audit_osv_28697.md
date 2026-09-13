# [H] usb: typec: ucsi: Limit read size on v1.2

## Summary
Severity: High
Advisory: CVE-2024-35924
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35924
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: ucsi: Limit read size on v1.2

Between UCSI 1.2 and UCSI 2.0, the size of the MESSAGE_IN region was
increased from 16 to 256. In order to avoid overflowing reads for older
systems, add a mechanism to use the read UCSI version to truncate read
sizes on UCSI v1.2.

## References
- https://git.kernel.org/stable/c/0defcaa09d3b21e8387829ee3a652c43fa91e13f
- https://git.kernel.org/stable/c/266f403ec47573046dee4bcebda82777ce702c40
- https://git.kernel.org/stable/c/b3db266fb031fba88c423d4bb8983a73a3db6527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35924.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
