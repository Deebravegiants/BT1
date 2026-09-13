# [M] CVE-2020-18899

## Summary
Severity: Medium
Advisory: CVE-2020-18899
Aliases: PYSEC-2021-879
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-19
Source: https://osv.dev/vulnerability/CVE-2020-18899
Type: osv

## Details
An uncontrolled memory allocation in DataBufdata(subBox.length-sizeof(box)) function of Exiv2 0.27 allows attackers to cause a denial of service (DOS) via a crafted input.

## References
- https://security.gentoo.org/glsa/202312-06
- https://github.com/Exiv2/exiv2/issues/742
- https://cwe.mitre.org/data/definitions/789.html
