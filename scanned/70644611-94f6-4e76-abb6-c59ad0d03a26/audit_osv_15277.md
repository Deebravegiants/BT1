# [H] CVE-2019-14924

## Summary
Severity: High
Advisory: CVE-2019-14924
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-10
Source: https://osv.dev/vulnerability/CVE-2019-14924
Type: osv

## Details
An issue was discovered in GCDWebServer before 3.5.3. The method moveItem in the GCDWebUploader class checks the FileExtension of newAbsolutePath but not oldAbsolutePath. By leveraging this vulnerability, an adversary can make an inaccessible file be available (the credential of the app, for instance).

## References
- https://github.com/swisspol/GCDWebServer/issues/433
- https://github.com/swisspol/GCDWebServer/commit/02738433bf2e1b820ef48f04edd15df304081802
- https://github.com/swisspol/GCDWebServer/compare/3.5.2...3.5.3
