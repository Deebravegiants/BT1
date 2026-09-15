# [M] CVE-2018-12467

## Summary
Severity: Medium
Advisory: CVE-2018-12467
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2018-12467
Type: osv

## Details
Authorized users of the openbuildservice before 2.9.4 could delete packages by using a malicious request against projects having the OBS:InitializeDevelPackage attribute, a similar issue to CVE-2018-7689.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1100217
- https://github.com/openSUSE/open-build-service/commit/f57b660f49f830006766a8d4abc3b4af6e178063
