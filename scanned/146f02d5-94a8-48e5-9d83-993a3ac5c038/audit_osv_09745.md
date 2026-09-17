# [M] CVE-2017-11328

## Summary
Severity: Medium
Advisory: CVE-2017-11328
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11328
Type: osv

## Details
Heap buffer overflow in the yr_object_array_set_item() function in object.c in YARA 3.x allows a denial-of-service attack by scanning a crafted .NET file.

## References
- https://github.com/VirusTotal/yara/commit/4a342f01e5439b9bb901aff1c6c23c536baeeb3f
