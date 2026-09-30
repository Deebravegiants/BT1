# [H] accel/ivpu: Prevent recovery invocation during probe and resume

## Summary
Severity: High
Advisory: CVE-2024-56540
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56540
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Prevent recovery invocation during probe and resume

Refactor IPC send and receive functions to allow correct
handling of operations that should not trigger a recovery process.

Expose ivpu_send_receive_internal(), which is now utilized by the D0i3
entry, DCT initialization, and HWS initialization functions.
These functions have been modified to return error codes gracefully,
rather than initiating recovery.

The updated functions are invoked within ivpu_probe() and ivpu_resume(),
ensuring that any errors encountered during these stages result in a proper
teardown or shutdown sequence. The previous approach of triggering recovery
within these functions could lead to a race condition, potentially causing
undefined behavior and kernel crashes due to null pointer dereferences.

## References
- https://git.kernel.org/stable/c/362ef76020ea6219a4df4ac5b738672b59527239
- https://git.kernel.org/stable/c/5eaa497411197c41b0813d61ba3fbd6267049082
- https://git.kernel.org/stable/c/cac822772c4dc27a285f09caf30072ab76d2bf38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56540.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56540
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
