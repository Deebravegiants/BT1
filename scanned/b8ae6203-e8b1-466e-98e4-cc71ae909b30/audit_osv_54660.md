# [H] CVE-2024-25443

## Summary
Severity: High
Advisory: CVE-2024-25443
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-25443
Type: osv

## Details
An issue in the HuginBase::ImageVariable<double>::linkWith function of Hugin v2022.0.0 allows attackers to cause a heap-use-after-free via parsing a crafted image.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NAV7IMHCOIMBEIW42KM2QUJ4MDQLNW3Z/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NAV7IMHCOIMBEIW42KM2QUJ4MDQLNW3Z/
- https://bugs.launchpad.net/hugin/+bug/2025035
