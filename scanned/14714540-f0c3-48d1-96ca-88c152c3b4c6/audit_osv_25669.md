# [M] Out-of-bounds read information disclosure vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-4135
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-4135
Type: osv

## Details
A heap out-of-bounds memory read flaw was found in the virtual nvme device in QEMU. The QEMU process does not validate an offset provided by the guest before computing a host heap pointer, which is used for copying data back to the guest. Arbitrary heap memory relative to an allocated buffer can be disclosed.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-4135
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4135.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4135
- https://security.netapp.com/advisory/ntap-20230915-0012/
- https://www.zerodayinitiative.com/advisories/ZDI-CAN-21521
- https://bugzilla.redhat.com/show_bug.cgi?id=2229101
