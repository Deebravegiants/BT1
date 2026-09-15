# [H] eth: fbnic: unlink NAPIs from queues on error to open

## Summary
Severity: High
Advisory: CVE-2025-38570
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38570
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: fbnic: unlink NAPIs from queues on error to open

CI hit a UaF in fbnic in the AF_XDP portion of the queues.py test.
The UaF is in the __sk_mark_napi_id_once() call in xsk_bind(),
NAPI has been freed. Looks like the device failed to open earlier,
and we lack clearing the NAPI pointer from the queue.

## References
- https://git.kernel.org/stable/c/21d3f8441c7f317b93ba6a8029610c8b7e3773db
- https://git.kernel.org/stable/c/4b31bcb025cb497da2b01f87173108ff32d350d2
- https://git.kernel.org/stable/c/4b59f9deff3bdb52b223c85048f1d2924803b817
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38570.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
