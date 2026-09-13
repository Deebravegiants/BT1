# [M] CVE-2023-3439

## Summary
Severity: Medium
Advisory: CVE-2023-3439
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-3439
Type: osv

## Details
A flaw was found in the MCTP protocol in the Linux kernel. The function mctp_unregister() reclaims the device's relevant resource when a netcard detaches. However, a running routine may be unaware of this and cause the use-after-free of the mdev->addrs object, potentially leading to a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3439.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3439
- https://bugzilla.redhat.com/show_bug.cgi?id=2217915
- https://github.com/torvalds/linux/commit/b561275d633bcd8e0e8055ab86f1a13df75a0269
- http://www.openwall.com/lists/oss-security/2023/07/02/1
