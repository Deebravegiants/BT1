# [H] CVE-2021-44142

## Summary
Severity: High
Advisory: CVE-2021-44142
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2021-44142
Type: osv

## Details
The Samba vfs_fruit module uses extended file attributes (EA, xattr) to provide "...enhanced compatibility with Apple SMB clients and interoperability with a Netatalk 3 AFP fileserver." Samba versions prior to 4.13.17, 4.14.12 and 4.15.5 with vfs_fruit configured allow out-of-bounds heap read and write via specially crafted extended file attributes. A remote attacker with write access to extended file attributes can execute arbitrary code with the privileges of smbd, typically root.

## References
- https://kb.cert.org/vuls/id/119678
- https://www.kb.cert.org/vuls/id/119678
- https://www.samba.org/samba/security/CVE-2021-44142.html
- https://security.gentoo.org/glsa/202309-06
- https://bugzilla.samba.org/show_bug.cgi?id=14914
- https://www.zerodayinitiative.com/blog/2022/2/1/cve-2021-44142-details-on-a-samba-code-execution-bug-demonstrated-at-pwn2own-austin
