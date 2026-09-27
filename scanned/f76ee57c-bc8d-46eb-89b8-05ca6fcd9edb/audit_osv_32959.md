# [C] bus: mhi: ep: Update read pointer only after buffer is written

## Summary
Severity: Critical
Advisory: CVE-2025-38429
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38429
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: ep: Update read pointer only after buffer is written

Inside mhi_ep_ring_add_element, the read pointer (rd_offset) is updated
before the buffer is written, potentially causing race conditions where
the host sees an updated read pointer before the buffer is actually
written. Updating rd_offset prematurely can lead to the host accessing
an uninitialized or incomplete element, resulting in data corruption.

Invoke the buffer write before updating rd_offset to ensure the element
is fully written before signaling its availability.

## References
- https://git.kernel.org/stable/c/0007ef098dab48f1ba58364c40b4809f1e21b130
- https://git.kernel.org/stable/c/44b9620e82bbec2b9a6ac77f63913636d84f96dc
- https://git.kernel.org/stable/c/6f18d174b73d0ceeaa341f46c0986436b3aefc9a
- https://git.kernel.org/stable/c/f704a80d9fa268e51a6cc5242714502c3c1fa605
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38429.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38429
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
