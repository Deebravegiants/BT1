# [H] CVE-2021-3738

## Summary
Severity: High
Advisory: CVE-2021-3738
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3738
Type: osv

## Details
In DCE/RPC it is possible to share the handles (cookies for resource state) between multiple connections via a mechanism called 'association groups'. These handles can reference connections to our sam.ldb database. However while the database was correctly shared, the user credentials state was only pointed at, and when one connection within that association group ended, the database would be left pointing at an invalid 'struct session_info'. The most likely outcome here is a crash, but it is possible that the use-after-free could instead allow different user state to be pointed at and this might allow more privileged access.

## References
- https://security.gentoo.org/glsa/202309-06
- https://www.samba.org/samba/security/CVE-2021-3738.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2021726
- https://bugzilla.samba.org/show_bug.cgi?id=14468
