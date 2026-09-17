# [H] CVE-2020-15953

## Summary
Severity: High
Advisory: CVE-2020-15953
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-07-27
Source: https://osv.dev/vulnerability/CVE-2020-15953
Type: osv

## Details
LibEtPan through 1.9.4, as used in MailCore 2 through 0.6.3 and other products, has a STARTTLS buffering issue that affects IMAP, SMTP, and POP3. When a server sends a "begin TLS" response, the client reads additional data (e.g., from a meddler-in-the-middle attacker) and evaluates it in a TLS context, aka "response injection."

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00075.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M65FVH5XPS23NLHFN3ABEGBSCHZAISXN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QFBWNA5REI5ZGW2DAOEAVHM23MOU6O5J/
- https://lists.debian.org/debian-lts-announce/2020/08/msg00026.html
- https://security.gentoo.org/glsa/202007-55
- https://github.com/dinhvh/libetpan/issues/386
