# [C] CVE-2024-38462

## Summary
Severity: Critical
Advisory: CVE-2024-38462
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-16
Source: https://osv.dev/vulnerability/CVE-2024-38462
Type: osv

## Details
iRODS before 4.3.2 provides an msiSendMail function with a problematic dependency on the mail binary, such as in the mailMS.cpp#L94-L106 reference.

## References
- https://github.com/irods/irods/blob/97eb33f130349db5e01a4b85e89dd1da81460345/server/re/src/mailMS.cpp#L94-L106
- https://irods.org/2024/05/irods-4-3-2-is-released/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38462.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38462
- https://github.com/irods/irods/issues/7562
- https://github.com/irods/irods/issues/7651
