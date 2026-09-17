# [H] CVE-2019-13723

## Summary
Severity: High
Advisory: CVE-2019-13723
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-13723
Type: osv

## Details
Use after free in WebBluetooth in Google Chrome prior to 78.0.3904.108 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/54XWRJ5LDFL27QXBPIBX3EHO4TPMKN4R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/USW7PGIHNPE6W3LGY6ZDFLELQGSL52CH/
- https://access.redhat.com/errata/RHSA-2019:3955
- https://chromereleases.googleblog.com/2019/11/stable-channel-update-for-desktop_18.html
- https://security.gentoo.org/glsa/202003-08
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00035.html
- https://crbug.com/1024121
