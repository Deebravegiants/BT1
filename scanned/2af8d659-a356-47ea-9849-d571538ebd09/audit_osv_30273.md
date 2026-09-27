# [M] clk: qcom: videocc-sm8350: use HW_CTRL_TRIGGER for vcodec GDSCs

## Summary
Severity: Medium
Advisory: CVE-2024-50266
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50266
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: qcom: videocc-sm8350: use HW_CTRL_TRIGGER for vcodec GDSCs

A recent change in the venus driver results in a stuck clock on the
Lenovo ThinkPad X13s, for example, when streaming video in firefox:

	video_cc_mvs0_clk status stuck at 'off'
	WARNING: CPU: 6 PID: 2885 at drivers/clk/qcom/clk-branch.c:87 clk_branch_wait+0x144/0x15c
	...
	Call trace:
	 clk_branch_wait+0x144/0x15c
	 clk_branch2_enable+0x30/0x40
	 clk_core_enable+0xd8/0x29c
	 clk_enable+0x2c/0x4c
	 vcodec_clks_enable.isra.0+0x94/0xd8 [venus_core]
	 coreid_power_v4+0x464/0x628 [venus_core]
	 vdec_start_streaming+0xc4/0x510 [venus_dec]
	 vb2_start_streaming+0x6c/0x180 [videobuf2_common]
	 vb2_core_streamon+0x120/0x1dc [videobuf2_common]
	 vb2_streamon+0x1c/0x6c [videobuf2_v4l2]
	 v4l2_m2m_ioctl_streamon+0x30/0x80 [v4l2_mem2mem]
	 v4l_streamon+0x24/0x30 [videodev]

using the out-of-tree sm8350/sc8280xp venus support. [1]

Update also the sm8350/sc8280xp GDSC definitions so that the hw control
mode can be changed at runtime as the venus driver now requires.

## References
- https://git.kernel.org/stable/c/d055f6f2bdfb8b9c9bc071f748c16bd3afb2db0f
- https://git.kernel.org/stable/c/f903663a8dcd6e1656e52856afbf706cc14cbe6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50266.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
