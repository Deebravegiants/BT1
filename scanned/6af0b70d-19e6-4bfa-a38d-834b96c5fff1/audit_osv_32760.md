# [H] pds_core: make wait_context part of q_info

## Summary
Severity: High
Advisory: CVE-2025-37886
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37886
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pds_core: make wait_context part of q_info

Make the wait_context a full part of the q_info struct rather
than a stack variable that goes away after pdsc_adminq_post()
is done so that the context is still available after the wait
loop has given up.

There was a case where a slow development firmware caused
the adminq request to time out, but then later the FW finally
finished the request and sent the interrupt.  The handler tried
to complete_all() the completion context that had been created
on the stack in pdsc_adminq_post() but no longer existed.
This caused bad pointer usage, kernel crashes, and much wailing
and gnashing of teeth.

## References
- https://git.kernel.org/stable/c/1d7c4b2b0bbfb09b55b2dc0e2355d7936bf89381
- https://git.kernel.org/stable/c/3f77c3dfffc7063428b100c4945ca2a7a8680380
- https://git.kernel.org/stable/c/520f012fe75fb8efc9f16a57ef929a7a2115d892
- https://git.kernel.org/stable/c/66d7702b42ffdf0dce4808626088268a4e905ca6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37886.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37886
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
