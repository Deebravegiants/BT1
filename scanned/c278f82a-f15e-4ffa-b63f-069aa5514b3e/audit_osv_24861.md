# [H] CVE-2023-27772

## Summary
Severity: High
Advisory: CVE-2023-27772
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-13
Source: https://osv.dev/vulnerability/CVE-2023-27772
Type: osv

## Details
libiec61850 v1.5.1 was discovered to contain a segmentation violation via the function ControlObjectClient_setOrigin() at /client/client_control.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27772.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27772
- https://github.com/mz-automation/libiec61850/issues/442
- https://github.com/mz-automation/libiec61850/commit/79a8eaf26070e02044afc4b2ffbfe777dfdf3e0b
