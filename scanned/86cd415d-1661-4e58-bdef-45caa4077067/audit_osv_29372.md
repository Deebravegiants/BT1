# [H] nvmet: fix a possible leak when destroy a ctrl during qp establishment

## Summary
Severity: High
Advisory: CVE-2024-42152
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42152
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: fix a possible leak when destroy a ctrl during qp establishment

In nvmet_sq_destroy we capture sq->ctrl early and if it is non-NULL we
know that a ctrl was allocated (in the admin connect request handler)
and we need to release pending AERs, clear ctrl->sqs and sq->ctrl
(for nvme-loop primarily), and drop the final reference on the ctrl.

However, a small window is possible where nvmet_sq_destroy starts (as
a result of the client giving up and disconnecting) concurrently with
the nvme admin connect cmd (which may be in an early stage). But *before*
kill_and_confirm of sq->ref (i.e. the admin connect managed to get an sq
live reference). In this case, sq->ctrl was allocated however after it was
captured in a local variable in nvmet_sq_destroy.
This prevented the final reference drop on the ctrl.

Solve this by re-capturing the sq->ctrl after all inflight request has
completed, where for sure sq->ctrl reference is final, and move forward
based on that.

This issue was observed in an environment with many hosts connecting
multiple ctrls simoutanuosly, creating a delay in allocating a ctrl
leading up to this race window.

## References
- https://git.kernel.org/stable/c/2f3c22b1d3d7e86712253244797a651998c141fa
- https://git.kernel.org/stable/c/5502c1f1d0d7472706cc1f201aecf1c935d302d1
- https://git.kernel.org/stable/c/818004f2a380420c19872171be716174d4985e33
- https://git.kernel.org/stable/c/940a71f08ef153ef807f751310b0648d1fa5d0da
- https://git.kernel.org/stable/c/b4fed1443a6571d49c6ffe7d97af3bbe5ee6dff5
- https://git.kernel.org/stable/c/c758b77d4a0a0ed3a1292b3fd7a2aeccd1a169a4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42152.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42152
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
