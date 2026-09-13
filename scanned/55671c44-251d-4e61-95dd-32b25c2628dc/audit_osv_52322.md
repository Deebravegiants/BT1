# [H] CVE-2021-47328

## Summary
Severity: High
Advisory: CVE-2021-47328
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47328
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: iscsi: Fix conn use after free during resets

If we haven't done a unbind target call we can race where
iscsi_conn_teardown wakes up the EH thread and then frees the conn while
those threads are still accessing the conn ehwait.

We can only do one TMF per session so this just moves the TMF fields from
the conn to the session. We can then rely on the
iscsi_session_teardown->iscsi_remove_session->__iscsi_unbind_session call
to remove the target and it's devices, and know after that point there is
no device or scsi-ml callout trying to access the session.

## References
- https://git.kernel.org/stable/c/ec29d0ac29be366450a7faffbcf8cba3a6a3b506
- https://git.kernel.org/stable/c/f0a031f7c55ffd944fead1ddaf2aa94df9a158c1
- https://git.kernel.org/stable/c/fa9542b35ceb4202e8f8d65f440529a63524dca9
- https://git.kernel.org/stable/c/89812e7957ab0746eab66ed6fc49d52bb4dca250
- https://git.kernel.org/stable/c/bf20d85a88384574fabb3d53ad62a8af57e7ab11
- https://git.kernel.org/stable/c/d04958a348e560938410e04a12fb99da9c7e6a00
