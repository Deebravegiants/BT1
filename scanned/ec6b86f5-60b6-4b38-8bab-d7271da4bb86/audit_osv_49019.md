# [M] CVE-2018-20449

## Summary
Severity: Medium
Advisory: CVE-2018-20449
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2018-20449
Type: osv

## Details
The hidma_chan_stats function in drivers/dma/qcom/hidma_dbg.c in the Linux kernel 4.14.90 allows local users to obtain sensitive address information by reading "callback=" lines in a debugfs file.

## References
- https://www.mail-archive.com/debian-security-tracker%40lists.debian.org/msg03808.html
- https://security.netapp.com/advisory/ntap-20190502-0002/
- https://elixir.bootlin.com/linux/v4.14.90/source/drivers/dma/qcom/hidma_dbg.c#L92
