# [C] CVE-2019-11921

## Summary
Severity: Critical
Advisory: CVE-2019-11921
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-11921
Type: osv

## Details
An out of bounds write is possible via a specially crafted packet in certain configurations of Proxygen due to improper handling of Base64 when parsing malformed binary content in Structured HTTP Headers. This issue affects versions of proxygen prior to v2019.07.22.00.

## References
- https://www.facebook.com/security/advisories/cve-2019-11921
- https://github.com/facebook/proxygen/commit/2f07985bef9fbae124cc63e5c0272e32da4fdaec
