# [M] Apache NimBLE: Lack of input validation in HCI advertising report could lead to potential out-of-bound access

## Summary
Severity: Medium
Advisory: CVE-2024-47250
CVSS: 5.0 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-47250
Type: osv

## Details
Out-of-bounds Read vulnerability in Apache NimBLE.

Missing proper validation of HCI advertising report could lead to out-of-bound access when parsing HCI event and thus bogus GAP 'device found' events being sent.
This issue requires broken or bogus Bluetooth controller and thus severity is considered low.
This issue affects Apache NimBLE: through 1.7.0.


Users are recommended to upgrade to version 1.8.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/26/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47250.json
- https://lists.apache.org/thread/zdb50spojlqbn0yxd866mbzqjt2vpt85
- https://nvd.nist.gov/vuln/detail/CVE-2024-47250
- https://github.com/apache/mynewt-nimble/commit/23d61150ddae4bc8356356d7ef09d816fb89da45
- https://github.com/apache/mynewt-nimble/commit/3b7a32ea09a3bffaab831ee0ab193a2375fc4df6
