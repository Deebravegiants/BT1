# [H] tracing: Have trace_event_file have ref counters

## Summary
Severity: High
Advisory: CVE-2023-52879
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52879
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.262, >=5.5.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Have trace_event_file have ref counters

The following can crash the kernel:

 # cd /sys/kernel/tracing
 # echo 'p:sched schedule' > kprobe_events
 # exec 5>>events/kprobes/sched/enable
 # > kprobe_events
 # exec 5>&-

The above commands:

 1. Change directory to the tracefs directory
 2. Create a kprobe event (doesn't matter what one)
 3. Open bash file descriptor 5 on the enable file of the kprobe event
 4. Delete the kprobe event (removes the files too)
 5. Close the bash file descriptor 5

The above causes a crash!

 BUG: kernel NULL pointer dereference, address: 0000000000000028
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: 0000 [#1] PREEMPT SMP PTI
 CPU: 6 PID: 877 Comm: bash Not tainted 6.5.0-rc4-test-00008-g2c6b6b1029d4-dirty #186
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.2-debian-1.16.2-1 04/01/2014
 RIP: 0010:tracing_release_file_tr+0xc/0x50

What happens here is that the kprobe event creates a trace_event_file
"file" descriptor that represents the file in tracefs to the event. It
maintains state of the event (is it enabled for the given instance?).
Opening the "enable" file gets a reference to the event "file" descriptor
via the open file descriptor. When the kprobe event is deleted, the file is
also deleted from the tracefs system which also frees the event "file"
descriptor.

But as the tracefs file is still opened by user space, it will not be
totally removed until the final dput() is called on it. But this is not
true with the event "file" descriptor that is already freed. If the user
does a write to or simply closes the file descriptor it will reference the
event "file" descriptor that was just freed, causing a use-after-free bug.

To solve this, add a ref count to the event "file" descriptor as well as a
new flag called "FREED". The "file" will not be freed until the last
reference is released. But the FREE flag will be set when the event is
removed to prevent any more modifications to that event from happening,
even if there's still a reference to the event "file" descriptor.

## References
- https://git.kernel.org/stable/c/2c9de867ca285c397cd71af703763fe416265706
- https://git.kernel.org/stable/c/2fa74d29fc1899c237d51bf9a6e132ea5c488976
- https://git.kernel.org/stable/c/9034c87d61be8cff989017740a91701ac8195a1d
- https://git.kernel.org/stable/c/961c4511c7578d6b8f39118be919016ec3db1c1e
- https://git.kernel.org/stable/c/a98172e36e5f1b3d29ad71fade2d611cfcc2fe6f
- https://git.kernel.org/stable/c/bb32500fb9b78215e4ef6ee8b4345c5f5d7eafb4
- https://git.kernel.org/stable/c/cbc7c29dff0fa18162f2a3889d82eeefd67305e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52879.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52879
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
