# [M] CVE-2021-47369

## Summary
Severity: Medium
Advisory: CVE-2021-47369
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47369
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/qeth: fix NULL deref in qeth_clear_working_pool_list()

When qeth_set_online() calls qeth_clear_working_pool_list() to roll
back after an error exit from qeth_hardsetup_card(), we are at risk of
accessing card->qdio.in_q before it was allocated by
qeth_alloc_qdio_queues() via qeth_mpc_initialize().

qeth_clear_working_pool_list() then dereferences NULL, and by writing to
queue->bufs[i].pool_entry scribbles all over the CPU's lowcore.
Resulting in a crash when those lowcore areas are used next (eg. on
the next machine-check interrupt).

Such a scenario would typically happen when the device is first set
online and its queues aren't allocated yet. An early IO error or certain
misconfigs (eg. mismatched transport mode, bad portno) then cause us to
error out from qeth_hardsetup_card() with card->qdio.in_q still being
NULL.

Fix it by checking the pointer for NULL before accessing it.

Note that we also have (rare) paths inside qeth_mpc_initialize() where
a configuration change can cause us to free the existing queues,
expecting that subsequent code will allocate them again. If we then
error out before that re-allocation happens, the same bug occurs.

Root-caused-by: Heiko Carstens <hca@linux.ibm.com>

## References
- https://git.kernel.org/stable/c/248f064af222a1f97ee02c84a98013dfbccad386
- https://git.kernel.org/stable/c/9b00fb12cdc9d8d1c3ffe82a78e74738127803fc
- https://git.kernel.org/stable/c/db94f89e1dadf693c15c2d60de0c34777cea5779
