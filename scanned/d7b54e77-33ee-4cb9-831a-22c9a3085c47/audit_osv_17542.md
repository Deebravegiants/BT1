# [M] CVE-2020-16144

## Summary
Severity: Medium
Advisory: CVE-2020-16144
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2020-16144
Type: osv

## Details
When using an object storage like S3 as the file store, when a user creates a public link to a folder where anonymous users can upload files, and another user uploads a virus the files antivirus app would detect the virus but fails to delete it due to permission issues. This affects the files_antivirus component versions before 0.15.2 for ownCloud.

## References
- https://owncloud.com/security-advisories/files-antivirus-doesnt-delete-virus-if-uploaded-through-public-link/
