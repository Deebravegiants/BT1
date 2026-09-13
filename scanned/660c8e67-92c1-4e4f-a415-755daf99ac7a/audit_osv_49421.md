# [H] CVE-2019-11755

## Summary
Severity: High
Advisory: CVE-2019-11755
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-11755
Type: osv

## Details
A crafted S/MIME message consisting of an inner encryption layer and an outer SignedData layer was shown as having a valid digital signature, although the signer might have had no access to the contents of the encrypted message, and might have stripped a different signature from the encrypted message. Previous versions had only suppressed showing a digital signature for messages with an outer multipart/signed layer. This vulnerability affects Thunderbird < 68.1.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- https://seclists.org/bugtraq/2019/Nov/24
- https://usn.ubuntu.com/4335-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00017.html
- https://usn.ubuntu.com/4202-1/
- https://www.debian.org/security/2019/dsa-4571
- https://www.mozilla.org/security/advisories/mfsa2019-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1240290
