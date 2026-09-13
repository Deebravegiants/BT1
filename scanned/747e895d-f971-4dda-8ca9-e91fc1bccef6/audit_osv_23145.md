# [C] CVE-2022-43634

## Summary
Severity: Critical
Advisory: CVE-2022-43634
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2022-43634
Type: osv

## Details
This vulnerability allows remote attackers to execute arbitrary code on affected installations of Netatalk. Authentication is not required to exploit this vulnerability. The specific flaw exists within the dsi_writeinit function. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length heap-based buffer. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-17646.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43634.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZYWSGVA6WXREMB6PV56HAHKU7R6KPOP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GEAFLA5L2SHOUFBAGUXIF2TZLGBXGJKT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SG6WZW5LXFVH3P7ZVZRGHUVJEMEFKQLI/
- https://nvd.nist.gov/vuln/detail/CVE-2022-43634
- https://www.debian.org/security/2023/dsa-5503
- https://www.zerodayinitiative.com/advisories/ZDI-23-094/
- https://github.com/Netatalk/Netatalk/pull/186
- https://lists.debian.org/debian-lts-announce/2023/05/msg00018.html
