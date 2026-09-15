# [H] CVE-2017-5594

## Summary
Severity: High
Advisory: CVE-2017-5594
Aliases: GHSA-rp89-32rp-qpq2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-25
Source: https://osv.dev/vulnerability/CVE-2017-5594
Type: osv

## Details
An issue was discovered in Pagekit CMS before 1.0.11. In this vulnerability the remote attacker is able to reset the registered user's password, when the debug toolbar is enabled. The password is successfully recovered using this exploit. The SecureLayer7 ID is SL7_PGKT_01.

## References
- http://www.securityfocus.com/bid/95806
- https://securelayer7.net/download/pdf/SecureLayer7-Pentest-report-Pagekit-CMS.pdf
- https://github.com/pagekit/pagekit/commit/e0454f9c037c427a5ff76a57e78dbf8cc00c268b
- https://securelayer7.net/download/poc/password-reset-vulnerability-exploit-ruby-pagekit-cms.rb.txt
- https://www.exploit-db.com/exploits/41143/
