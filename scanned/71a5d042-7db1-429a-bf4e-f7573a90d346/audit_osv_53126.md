# [H] CVE-2022-30256

## Summary
Severity: High
Advisory: CVE-2022-30256
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-11-19
Source: https://osv.dev/vulnerability/CVE-2022-30256
Type: osv

## Details
An issue was discovered in MaraDNS Deadwood through 3.5.0021 that allows variant V1 of unintended domain name resolution. A revoked domain name can still be resolvable for a long time, including expired domains and taken-down malicious domains. The effects of an exploit would be widespread and highly impactful, because the exploitation conforms to de facto DNS specifications and operational practices, and overcomes current mitigation patches for "Ghost" domain names.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3VSMLJX25MXGQ6A7UPOGK7VPUVDESPHL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NB7LDZM5AGWC5BHHQHW6CP5OFNBBKFOQ/
- https://maradns.samiam.org/
- https://maradns.samiam.org/security.html#CVE-2022-30256
- https://www.debian.org/security/2023/dsa-5441
