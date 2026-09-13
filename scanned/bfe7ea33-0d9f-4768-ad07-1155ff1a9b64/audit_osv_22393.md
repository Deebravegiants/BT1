# [M] CVE-2022-28352

## Summary
Severity: Medium
Advisory: CVE-2022-28352
CVSS: 4.3 (CVSS:3.1/AC:L/AV:N/A:N/C:L/I:N/PR:N/S:U/UI:R)
Published: 2022-04-02
Source: https://osv.dev/vulnerability/CVE-2022-28352
Type: osv

## Details
WeeChat (aka Wee Enhanced Environment for Chat) 3.2 to 3.4 before 3.4.1 does not properly verify the TLS certificate of the server, after certain GnuTLS options are changed, which allows man-in-the-middle attackers to spoof a TLS chat server via an arbitrary certificate. NOTE: this only affects situations where weechat.network.gnutls_ca_system or weechat.network.gnutls_ca_user is changed without a WeeChat restart.

## References
- https://weechat.org/doc/security/WSA-2022-1/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/28xxx/CVE-2022-28352.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-28352
- https://github.com/weechat/weechat/issues/1763
