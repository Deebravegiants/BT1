# [M] CVE-2021-47502

## Summary
Severity: Medium
Advisory: CVE-2021-47502
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47502
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: codecs: wcd934x: handle channel mappping list correctly

Currently each channel is added as list to dai channel list, however
there is danger of adding same channel to multiple dai channel list
which endups corrupting the other list where its already added.

This patch ensures that the channel is actually free before adding to
the dai channel list and also ensures that the channel is on the list
before deleting it.

This check was missing previously, and we did not hit this issue as
we were testing very simple usecases with sequence of amixer commands.

## References
- https://git.kernel.org/stable/c/1089dac26c6b4b833323ae6c0ceab29fb30ede72
- https://git.kernel.org/stable/c/23ba28616d3063bd4c4953598ed5e439ca891101
- https://git.kernel.org/stable/c/339ffb5b56005582aacc860524d2d208604049d1
