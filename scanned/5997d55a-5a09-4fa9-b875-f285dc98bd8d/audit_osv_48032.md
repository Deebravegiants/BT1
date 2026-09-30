# [H] CVE-2017-17497

## Summary
Severity: High
Advisory: CVE-2017-17497
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-10
Source: https://osv.dev/vulnerability/CVE-2017-17497
Type: osv

## Details
In Tidy 5.7.0, the prvTidyTidyMetaCharset function in clean.c allows attackers to cause a denial of service (Segmentation Fault), because the currentNode variable in the "children of the head" processing feature is modified in the loop without validating the new value.

## References
- https://github.com/htacg/tidy-html5/issues/656
