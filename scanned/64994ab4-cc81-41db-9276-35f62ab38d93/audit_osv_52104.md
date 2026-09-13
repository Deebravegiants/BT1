# [M] CVE-2021-47075

## Summary
Severity: Medium
Advisory: CVE-2021-47075
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47075
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: fix memory leak in nvmet_alloc_ctrl()

When creating ctrl in nvmet_alloc_ctrl(), if the cntlid_min is larger
than cntlid_max of the subsystem, and jumps to the
"out_free_changed_ns_list" label, but the ctrl->sqs lack of be freed.
Fix this by jumping to the "out_free_sqs" label.

## References
- https://git.kernel.org/stable/c/4720f29acb3fe67aa8aa71e6b675b079d193aaeb
- https://git.kernel.org/stable/c/afb680ed7ecbb7fd66ddb43650e9b533fd8b4b9a
- https://git.kernel.org/stable/c/fec356a61aa3d3a66416b4321f1279e09e0f256f
