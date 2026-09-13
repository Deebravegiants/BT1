# [M] CVE-2023-31082

## Summary
Severity: Medium
Advisory: CVE-2023-31082
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-31082
Type: osv

## Details
An issue was discovered in drivers/tty/n_gsm.c in the Linux kernel 6.2. There is a sleeping function called from an invalid context in gsmld_write, which will block the kernel. Note: This has been disputed by 3rd parties as not a valid vulnerability.

## References
- https://lore.kernel.org/all/CA+UBctCZok5FSQ=LPRA+A-jocW=L8FuMVZ_7MNqhh483P5yN8A%40mail.gmail.com/
- https://security.netapp.com/advisory/ntap-20230929-0003/
- https://bugzilla.suse.com/show_bug.cgi?id=1210781
