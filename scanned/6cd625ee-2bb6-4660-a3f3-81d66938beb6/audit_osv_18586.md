# [C] CVE-2020-28645

## Summary
Severity: Critical
Advisory: CVE-2020-28645
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2020-28645
Type: osv

## Details
Deleting users with certain names caused system files to be deleted. Risk is higher for systems which allow users to register themselves and have the data directory in the web root. This affects ownCloud/core versions < 10.6.

## References
- https://owncloud.com/security-advisories/missing-user-validation-leading-to-information-disclosure/
