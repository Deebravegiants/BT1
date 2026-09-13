# [M] CVE-2020-22916

## Summary
Severity: Medium
Advisory: CVE-2020-22916
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-22916
Type: osv

## Details
An issue discovered in XZ 5.2.5 allows attackers to cause a denial of service via decompression of a crafted file. NOTE: the vendor disputes the claims of "endless output" and "denial of service" because decompression of the 17,486 bytes always results in 114,881,179 bytes, which is often a reasonable size increase.

## References
- http://web.archive.org/web/20230918084612/https://github.com/snappyJack/CVE-request-XZ-5.2.5-has-denial-of-service-vulnerability
- https://security-tracker.debian.org/tracker/CVE-2020-22916
- https://tukaani.org/xz/
- https://bugzilla.redhat.com/show_bug.cgi?id=2234987
- https://bugzilla.suse.com/show_bug.cgi?id=1214590
- https://github.com/tukaani-project/xz/issues/61
- https://github.com/snappyJack/CVE-request-XZ-5.2.5-has-denial-of-service-vulnerability
