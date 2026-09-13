# [M] CVE-2022-0396

## Summary
Severity: Medium
Advisory: CVE-2022-0396
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2022-0396
Type: osv

## Details
BIND 9.16.11 -> 9.16.26, 9.17.0 -> 9.18.0 and versions 9.16.11-S1 -> 9.16.26-S1 of the BIND Supported Preview Edition. Specifically crafted TCP streams can cause connections to BIND to remain in CLOSE_WAIT status for an indefinite period of time, even after the client has terminated the connection.

## References
- https://kb.isc.org/v1/docs/cve-2022-0396
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NYD7US4HZRFUGAJ66ZTHFBYVP5N3OQBY/
- https://security.gentoo.org/glsa/202210-25
- https://security.netapp.com/advisory/ntap-20220408-0001/
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
