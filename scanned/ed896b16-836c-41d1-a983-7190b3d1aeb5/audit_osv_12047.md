# [C] CVE-2018-1000838

## Summary
Severity: Critical
Advisory: CVE-2018-1000838
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000838
Type: osv

## Details
autopsy version <= 4.9.0 contains a XML External Entity (XXE) vulnerability in CaseMetadata XML Parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via Specially crafted CaseMetadata.

## References
- https://0dd.zone/2018/10/28/autopsy-XXE/
- https://github.com/sleuthkit/autopsy/issues/4236
