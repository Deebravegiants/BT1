# [M] CVE-2020-36787

## Summary
Severity: Medium
Advisory: CVE-2020-36787
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36787
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: aspeed: fix clock handling logic

Video engine uses eclk and vclk for its clock sources and its reset
control is coupled with eclk so the current clock enabling sequence works
like below.

 Enable eclk
 De-assert Video Engine reset
 10ms delay
 Enable vclk

It introduces improper reset on the Video Engine hardware and eventually
the hardware generates unexpected DMA memory transfers that can corrupt
memory region in random and sporadic patterns. This issue is observed
very rarely on some specific AST2500 SoCs but it causes a critical
kernel panic with making a various shape of signature so it's extremely
hard to debug. Moreover, the issue is observed even when the video
engine is not actively used because udevd turns on the video engine
hardware for a short time to make a query in every boot.

To fix this issue, this commit changes the clock handling logic to make
the reset de-assertion triggered after enabling both eclk and vclk. Also,
it adds clk_unprepare call for a case when probe fails.

clk: ast2600: fix reset settings for eclk and vclk
Video engine reset setting should be coupled with eclk to match it
with the setting for previous Aspeed SoCs which is defined in
clk-aspeed.c since all Aspeed SoCs are sharing a single video engine
driver. Also, reset bit 6 is defined as 'Video Engine' reset in
datasheet so it should be de-asserted when eclk is enabled. This
commit fixes the setting.

## References
- https://git.kernel.org/stable/c/1dc1d30ac101bb8335d9852de2107af60c2580e7
- https://git.kernel.org/stable/c/2964c37563e86cfdc439f217eb3c5a69adfdba6a
- https://git.kernel.org/stable/c/3536169f8531c2c5b153921dc7d1ac9fd570cda7
- https://git.kernel.org/stable/c/75321dc8aebe3f30eff226028fe6da340fe0bf02
- https://git.kernel.org/stable/c/a59d01384c80a8a4392665802df57c3df20055f5
