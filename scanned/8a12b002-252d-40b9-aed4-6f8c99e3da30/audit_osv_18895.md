# [M] CVE-2020-36855

## Summary
Severity: Medium
Advisory: CVE-2020-36855
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/CVE-2020-36855
Type: osv

## Details
A security vulnerability has been detected in DCMTK up to 3.6.5. The affected element is the function parseQuota of the component dcmqrscp. The manipulation of the argument StorageQuota leads to stack-based buffer overflow. Local access is required to approach this attack. The exploit has been disclosed publicly and may be used. Upgrading to version 3.6.6 is sufficient to fix this issue. The identifier of the patch is 0fef9f02e. It is recommended to upgrade the affected component.

## References
- https://vuldb.com/?id.329028
- https://vuldb.com/?submit.673137
- https://vuldb.com/?ctiid.329028
- https://shimo.im/docs/rp3OMVMDPKtjn0km/
- https://shimo.im/docs/rp3OMVMDPKtjn0km/read
