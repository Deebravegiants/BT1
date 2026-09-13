# [H] CVE-2024-26529

## Summary
Severity: High
Advisory: CVE-2024-26529
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-13
Source: https://osv.dev/vulnerability/CVE-2024-26529
Type: osv

## Details
An issue in mz-automation libiec61850 v.1.5.3 and before, allows a remote attacker to cause a denial of service (DoS) via the mmsServer_handleDeleteNamedVariableListRequest function of src/mms/iso_mms/server/mms_named_variable_list_service.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26529.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26529
- https://github.com/mz-automation/libiec61850/issues/492
- https://github.com/mz-automation/libiec61850/issues/495
