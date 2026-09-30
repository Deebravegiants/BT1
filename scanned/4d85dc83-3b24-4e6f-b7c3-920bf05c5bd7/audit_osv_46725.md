# [H] CVE-2014-9888

## Summary
Severity: High
Advisory: CVE-2014-9888
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2014-9888
Type: osv

## Details
arch/arm/mm/dma-mapping.c in the Linux kernel before 3.13 on ARM platforms, as used in Android before 2016-08-05 on Nexus 5 and 7 (2013) devices, does not prevent executable DMA mappings, which might allow local users to gain privileges via a crafted application, aka Android internal bug 28803642 and Qualcomm internal bug CR642735.

## References
- http://source.android.com/security/bulletin/2016-08-01.html
- https://github.com/torvalds/linux/commit/0ea1ec713f04bdfac343c9702b21cd3a7c711826
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0ea1ec713f04bdfac343c9702b21cd3a7c711826
- http://source.android.com/security/bulletin/2016-08-01.html
- http://www.securityfocus.com/bid/92219
- https://source.codeaurora.org/quic/la/kernel/msm/commit/?id=f044936caab337a4384fbfe64a4cbae33c7e22a1
