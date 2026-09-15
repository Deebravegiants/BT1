# [H] CVE-2025-1713

## Summary
Severity: High
Advisory: CVE-2025-1713
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-1713
Type: osv

## Details
When setting up interrupt remapping for legacy PCI(-X) devices,
including PCI(-X) bridges, a lookup of the upstream bridge is required.
This lookup, itself involving acquiring of a lock, is done in a context
where acquiring that lock is unsafe.  This can lead to a deadlock.

## References
- http://www.openwall.com/lists/oss-security/2025/02/27/3
- http://www.openwall.com/lists/oss-security/2025/02/28/1
- http://www.openwall.com/lists/oss-security/2025/02/27/1
- http://xenbits.xen.org/xsa/advisory-467.html
- https://xenbits.xenproject.org/xsa/advisory-467.html
