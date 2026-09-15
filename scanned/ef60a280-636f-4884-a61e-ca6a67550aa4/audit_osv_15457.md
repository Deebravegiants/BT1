# [C] CVE-2019-16378

## Summary
Severity: Critical
Advisory: CVE-2019-16378
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-17
Source: https://osv.dev/vulnerability/CVE-2019-16378
Type: osv

## Details
OpenDMARC through 1.3.2 and 1.4.x through 1.4.0-Beta1 is prone to a signature-bypass vulnerability with multiple From: addresses, which might affect applications that consider a domain name to be relevant to the origin of an e-mail message.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6HEWDFGRKQHIWKFZH5BNWQDGUPNR7VH3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PEUBIHJLMPMB6KHOSGDMUQKSAW4HOCYM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y7RT6ID7MBCEPNZEIUKK2TZIOCYPJR6E/
- https://bugs.debian.org/940081
- https://seclists.org/bugtraq/2019/Sep/36
- https://usn.ubuntu.com/4567-1/
- https://www.debian.org/security/2019/dsa-4526
- https://www.openwall.com/lists/oss-security/2019/09/11/8
- https://github.com/trusteddomainproject/OpenDMARC/pull/48
- http://www.openwall.com/lists/oss-security/2019/09/17/2
