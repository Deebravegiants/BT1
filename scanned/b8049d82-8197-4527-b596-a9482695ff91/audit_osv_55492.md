# [C] CVE-2025-58143

## Summary
Severity: Critical
Advisory: CVE-2025-58143
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-58143
Type: osv

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

There are multiple issues related to the handling and accessing of guest
memory pages in the viridian code:

 1. A NULL pointer dereference in the updating of the reference TSC area.
    This is CVE-2025-27466.

 2. A NULL pointer dereference by assuming the SIM page is mapped when
    a synthetic timer message has to be delivered.  This is
    CVE-2025-58142.

 3. A race in the mapping of the reference TSC page, where a guest can
    get Xen to free a page while still present in the guest physical to
    machine (p2m) page tables.  This is CVE-2025-58143.

## References
- http://www.openwall.com/lists/oss-security/2025/09/09/1
- https://xenbits.xenproject.org/xsa/advisory-472.html
- http://xenbits.xen.org/xsa/advisory-472.html
