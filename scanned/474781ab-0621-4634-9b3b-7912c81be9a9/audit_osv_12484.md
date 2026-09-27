# [H] CVE-2018-12473

## Summary
Severity: High
Advisory: CVE-2018-12473
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-02
Source: https://osv.dev/vulnerability/CVE-2018-12473
Type: osv

## Details
A path traversal traversal vulnerability in obs-service-tar_scm of Open Build Service allows remote attackers to cause access files not in the current build. On the server itself this is prevented by confining the worker via KVM. Affected releases are openSUSE Open Build Service: versions prior to 70d1aa4cc4d7b940180553a63805c22fc62e2cf0.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1105361
- https://github.com/openSUSE/obs-service-tar_scm/pull/248
