# [H] BIT-node-2023-38552

## Summary
Severity: High
Advisory: BIT-node-2023-38552
Aliases: BIT-node-min-2023-38552, CVE-2023-38552
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2023-38552
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <20.8.1

## Details
When the Node.js policy feature checks the integrity of a resource against a trusted manifest, the application can intercept the operation and return a forged checksum to the node's policy implementation, thus effectively disabling the integrity check.
Impacts:
This vulnerability affects all users using the experimental policy mechanism in all active release lines: 18.x and, 20.x.
Please note that at the time this CVE was issued, the policy mechanism is an experimental feature of Node.js.

## References
- https://hackerone.com/reports/2094235
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3N4NJ7FR4X4FPZUGNTQAPSTVB2HB2Y4A/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/E72T67UPDRXHIDLO3OROR25YAMN4GGW5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FNA62Q767CFAFHBCDKYNPBMZWB7TWYVU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HT7T2R4MQKLIF4ODV4BDLPARWFPCJ5CZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LKYHSZQFDNR7RSA7LHVLLIAQMVYCUGBG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X6QXN4ORIVF6XBW4WWFE7VNPVC74S45Y/
- https://security.netapp.com/advisory/ntap-20231116-0013/
- https://nvd.nist.gov/vuln/detail/CVE-2023-38552
- https://security.netapp.com/advisory/ntap-20241108-0002/
