# [H] CVE-2016-8520

## Summary
Severity: High
Advisory: CVE-2016-8520
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8520
Type: osv

## Details
HPE Helion Eucalyptus v4.3.0 and earlier does not correctly check IAM user's permissions for accessing versioned objects and ACLs. In some cases, authenticated users with S3 permissions could also access versioned data.

## References
- http://www.securityfocus.com/bid/95369
- https://support.hpe.com/hpsc/doc/public/display?docId=emr_na-c05363782
