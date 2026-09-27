# [H] CVE-2021-42614

## Summary
Severity: High
Advisory: CVE-2021-42614
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-24
Source: https://osv.dev/vulnerability/CVE-2021-42614
Type: osv

## Details
A use after free in info_width_internal in bk_info.c in Halibut 1.2 allows an attacker to cause a segmentation fault or possibly have unspecified other impact via a crafted text document.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CC7UZ7NRXDA7YSCSGWE2CBQM7OZS3K2R/
- https://carteryagemann.com/halibut-case-study.html#poc-halibut-info-uaf
