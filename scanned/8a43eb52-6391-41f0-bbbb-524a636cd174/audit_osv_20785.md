# [H] CVE-2021-3697

## Summary
Severity: High
Advisory: CVE-2021-3697
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2021-3697
Type: osv

## Details
A crafted JPEG image may lead the JPEG reader to underflow its data pointer, allowing user-controlled data to be written in heap. To a successful to be performed the attacker needs to perform some triage over the heap layout and craft an image with a malicious format and payload. This vulnerability can lead to data corruption and eventual code execution or secure boot circumvention. This flaw affects grub2 versions prior grub-2.12.

## References
- https://security.gentoo.org/glsa/202209-12
- https://security.netapp.com/advisory/ntap-20220930-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1991687
