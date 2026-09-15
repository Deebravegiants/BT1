# [M] CVE-2021-45846

## Summary
Severity: Medium
Advisory: CVE-2021-45846
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-25
Source: https://osv.dev/vulnerability/CVE-2021-45846
Type: osv

## Details
A flaw in the AMF parser of Slic3r libslic3r 1.3.0 allows an attacker to cause an application crash using a crafted AMF document, where a metadata tag lacks a "type" attribute.

## References
- https://github.com/slic3r/Slic3r/issues/5117
