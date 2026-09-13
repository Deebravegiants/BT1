# [M] Autolab has vulnerable submission endpoints

## Summary
Severity: Medium
Advisory: CVE-2024-52584
Aliases: GHSA-rjg4-cf66-x6gr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-52584
Type: osv

## Details
Autolab is a course management service that enables auto-graded programming assignments. There is a vulnerability in version 3.0.1 where CAs can view or edit the grade for any submission ID, even if they are not a CA for the class that has the submission. The endpoints only check that the CAs have the authorization level of a CA in the class in the endpoint, which is not necessarily the class the submission is attached to. Version 3.0.2 contains a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52584.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-rjg4-cf66-x6gr
- https://nvd.nist.gov/vuln/detail/CVE-2024-52584
- https://github.com/autolab/Autolab/commit/96006d532a392eeca2d350d1811f8e8ab9625bda
