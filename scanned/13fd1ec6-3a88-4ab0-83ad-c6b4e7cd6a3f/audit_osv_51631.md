# [C] CVE-2021-3657

## Summary
Severity: Critical
Advisory: CVE-2021-3657
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-3657
Type: osv

## Details
A flaw was found in mbsync versions prior to 1.4.4. Due to inadequate handling of extremely large (>=2GiB) IMAP literals, malicious or compromised IMAP servers, and hypothetically even external email senders, could cause several different buffer overflows, which could conceivably be exploited for remote code execution.

## References
- https://www.openwall.com/lists/oss-security/2021/12/03/1
- https://lists.debian.org/debian-lts-announce/2022/07/msg00001.html
- https://security.gentoo.org/glsa/202208-15
- https://bugzilla.redhat.com/show_bug.cgi?id=2028932
