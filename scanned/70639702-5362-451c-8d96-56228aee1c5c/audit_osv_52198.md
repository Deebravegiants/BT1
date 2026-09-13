# [M] CVE-2021-47187

## Summary
Severity: Medium
Advisory: CVE-2021-47187
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47187
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: dts: qcom: msm8998: Fix CPU/L2 idle state latency and residency

The entry/exit latency and minimum residency in state for the idle
states of MSM8998 were ..bad: first of all, for all of them the
timings were written for CPU sleep but the min-residency-us param
was miscalculated (supposedly, while porting this from downstream);
Then, the power collapse states are setting PC on both the CPU
cluster *and* the L2 cache, which have different timings: in the
specific case of L2 the times are higher so these ones should be
taken into account instead of the CPU ones.

This parameter misconfiguration was not giving particular issues
because on MSM8998 there was no CPU scaling at all, so cluster/L2
power collapse was rarely (if ever) hit.
When CPU scaling is enabled, though, the wrong timings will produce
SoC unstability shown to the user as random, apparently error-less,
sudden reboots and/or lockups.

This set of parameters are stabilizing the SoC when CPU scaling is
ON and when power collapse is frequently hit.

## References
- https://git.kernel.org/stable/c/118c826ef8b43efe0fda8faf419673707ee8c5e5
- https://git.kernel.org/stable/c/3f1dcaff642e75c1d2ad03f783fa8a3b1f56dd50
- https://git.kernel.org/stable/c/a14d7038ea201c5526375becfc43b9ba281b1e82
- https://git.kernel.org/stable/c/e52fecdd0c142b95c720683885b06ee3f0e065c8
