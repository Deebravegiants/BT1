# [H] CVE-2022-45919

## Summary
Severity: High
Advisory: CVE-2022-45919
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-27
Source: https://osv.dev/vulnerability/CVE-2022-45919
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.10. In drivers/media/dvb-core/dvb_ca_en50221.c, a use-after-free can occur is there is a disconnect after an open, because of the lack of a wait_event.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=280a8ab81733da8bc442253c700a52c4c0886ffd
- https://lore.kernel.org/linux-media/20221121063308.GA33821%40ubuntu/T/#u
- https://security.netapp.com/advisory/ntap-20230113-0008/
