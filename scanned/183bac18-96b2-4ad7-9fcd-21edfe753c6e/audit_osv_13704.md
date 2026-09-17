# [C] CVE-2018-21029

## Summary
Severity: Critical
Advisory: CVE-2018-21029
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-30
Source: https://osv.dev/vulnerability/CVE-2018-21029
Type: osv

## Details
systemd 239 through 245 accepts any certificate signed by a trusted certificate authority for DNS Over TLS. Server Name Indication (SNI) is not sent, and there is no hostname validation with the GnuTLS backend. NOTE: This has been disputed by the developer as not a vulnerability since hostname validation does not have anything to do with this issue (i.e. there is no hostname to be sent)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4NLJVOJMB6ANDILRLDZK26YGLYBEPHKY/
- https://blog.cloudflare.com/dns-encryption-explained/
- https://security.netapp.com/advisory/ntap-20191122-0002/
- https://tools.ietf.org/html/rfc7858#section-4.1
- https://github.com/systemd/systemd/issues/9397
- https://github.com/systemd/systemd/blob/v243/src/resolve/resolved-dnstls-gnutls.c#L62-L63
- https://github.com/systemd/systemd/pull/13870
- https://github.com/systemd/systemd/blob/v239/man/resolved.conf.xml#L199-L207
- https://github.com/systemd/systemd/blob/v243/man/resolved.conf.xml#L196-L207
