# [H] CVE-2018-12684

## Summary
Severity: High
Advisory: CVE-2018-12684
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-06-22
Source: https://osv.dev/vulnerability/CVE-2018-12684
Type: osv

## Details
Out-of-bounds Read in the send_ssi_file function in civetweb.c in CivetWeb through 1.10 allows attackers to cause a Denial of Service or Information Disclosure via a crafted SSI file.

## References
- https://github.com/civetweb/civetweb/issues/633
- https://github.com/civetweb/civetweb/commit/8fd069f6dedb064339f1091069ac96f3f8bdb552
