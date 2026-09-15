# [M] CVE-2020-14383

## Summary
Severity: Medium
Advisory: CVE-2020-14383
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-14383
Type: osv

## Details
A flaw was found in samba's DNS server. An authenticated user could use this flaw to the RPC server to crash. This RPC server, which also serves protocols other than dnsserver, will be restarted after a short delay, but it is easy for an authenticated non administrative attacker to crash it again as soon as it returns. The Samba DNS server itself will continue to operate, but many RPC services will not.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
- https://security.gentoo.org/glsa/202012-24
- https://www.samba.org/samba/security/CVE-2020-14383.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1892636
