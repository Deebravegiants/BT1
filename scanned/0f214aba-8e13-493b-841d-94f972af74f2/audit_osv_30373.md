# [H] Apache NimBLE: Lack of input sanitization leading to out-of-bound reads in Number of Completed Packets HCI event handler

## Summary
Severity: High
Advisory: CVE-2024-51569
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-51569
Type: osv

## Details
Out-of-bounds Read vulnerability in Apache NimBLE.

Missing proper validation of HCI Number Of Completed Packets could lead to out-of-bound access when parsing HCI event and invalid read from HCI transport memory.
This issue requires broken or bogus Bluetooth controller and thus severity is considered low.
This issue affects Apache NimBLE: through 1.7.0.


Users are recommended to upgrade to version 1.8.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/26/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51569.json
- https://lists.apache.org/thread/q0vs5rddx1lho30xnpsrvpzgxqmywnhs
- https://nvd.nist.gov/vuln/detail/CVE-2024-51569
- https://github.com/apache/mynewt-nimble/commit/4e3ac5b6e7c7df63a594c4ff6839e266b4ccfed9
