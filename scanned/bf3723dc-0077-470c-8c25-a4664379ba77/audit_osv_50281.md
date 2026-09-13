# [M] CVE-2020-10759

## Summary
Severity: Medium
Advisory: CVE-2020-10759
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-10759
Type: osv

## Details
A PGP signature bypass flaw was found in fwupd (all versions), which could lead to the installation of unsigned firmware. As per upstream, a signature bypass is theoretically possible, but not practical because the Linux Vendor Firmware Service (LVFS) is either not implemented or enabled in versions of fwupd shipped with Red Hat Enterprise Linux 7 and 8. The highest threat from this vulnerability is to confidentiality and integrity.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1844316
- https://github.com/justinsteven/advisories/blob/master/2020_fwupd_dangling_s3_bucket_and_CVE-2020-10759_signature_verification_bypass.md
