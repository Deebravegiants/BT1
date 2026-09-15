# [H] scsi: target: Fix multiple LUN_RESET handling

## Summary
Severity: High
Advisory: CVE-2023-53586
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53586
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: Fix multiple LUN_RESET handling

This fixes a bug where an initiator thinks a LUN_RESET has cleaned up
running commands when it hasn't. The bug was added in commit 51ec502a3266
("target: Delete tmr from list before processing").

The problem occurs when:

 1. We have N I/O cmds running in the target layer spread over 2 sessions.

 2. The initiator sends a LUN_RESET for each session.

 3. session1's LUN_RESET loops over all the running commands from both
    sessions and moves them to its local drain_task_list.

 4. session2's LUN_RESET does not see the LUN_RESET from session1 because
    the commit above has it remove itself. session2 also does not see any
    commands since the other reset moved them off the state lists.

 5. sessions2's LUN_RESET will then complete with a successful response.

 6. sessions2's inititor believes the running commands on its session are
    now cleaned up due to the successful response and cleans up the running
    commands from its side. It then restarts them.

 7. The commands do eventually complete on the backend and the target
    starts to return aborted task statuses for them. The initiator will
    either throw a invalid ITT error or might accidentally lookup a new
    task if the ITT has been reallocated already.

Fix the bug by reverting the patch, and serialize the execution of
LUN_RESETs and Preempt and Aborts.

Also prevent us from waiting on LUN_RESETs in core_tmr_drain_tmr_list,
because it turns out the original patch fixed a bug that was not
mentioned. For LUN_RESET1 core_tmr_drain_tmr_list can see a second
LUN_RESET and wait on it. Then the second reset will run
core_tmr_drain_tmr_list and see the first reset and wait on it resulting in
a deadlock.

## References
- https://git.kernel.org/stable/c/2c43de56f9220dca3e28c774d1c5e2cab574223a
- https://git.kernel.org/stable/c/673db054d7a2b5a470d7a25baf65956d005ad729
- https://git.kernel.org/stable/c/9158c86fd3237acaea8f0181c7836d90fd6eea10
- https://git.kernel.org/stable/c/e1f59cd18a10969d08a082264b557876ca38766e
- https://git.kernel.org/stable/c/eacfe32c3650bfd0e54224d160c431013d7f6998
- https://git.kernel.org/stable/c/ed18526289b5603bf2253dee50f1d7ec245cf397
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53586.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
