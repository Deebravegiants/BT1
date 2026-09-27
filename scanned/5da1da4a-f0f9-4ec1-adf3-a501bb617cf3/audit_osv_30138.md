# [M] ASoC: qcom: sc7280: Fix missing Soundwire runtime stream alloc

## Summary
Severity: Medium
Advisory: CVE-2024-50105
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50105
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: qcom: sc7280: Fix missing Soundwire runtime stream alloc

Commit 15c7fab0e047 ("ASoC: qcom: Move Soundwire runtime stream alloc to
soundcards") moved the allocation of Soundwire stream runtime from the
Qualcomm Soundwire driver to each individual machine sound card driver,
except that it forgot to update SC7280 card.

Just like for other Qualcomm sound cards using Soundwire, the card
driver should allocate and release the runtime.  Otherwise sound
playback will result in a NULL pointer dereference or other effect of
uninitialized memory accesses (which was confirmed on SDM845 having
similar issue).

## References
- https://git.kernel.org/stable/c/176a41ebec42a921277cd34e8c0c2e776a9dd6c4
- https://git.kernel.org/stable/c/db7e59e6a39a4d3d54ca8197c796557e6d480b0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50105.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
