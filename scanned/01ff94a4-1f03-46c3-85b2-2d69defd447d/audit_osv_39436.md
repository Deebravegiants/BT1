# [M] MyBB: Default CAPTCHA missing invalidation

## Summary
Severity: Medium
Advisory: CVE-2026-45734
Aliases: GHSA-jrrr-f3jw-mjmc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45734
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the built-in CAPTCHA does not consistently enforce single-use semantics, allowing remote attackers to bypass CAPTCHA controls through challenge replay. The successful validation paths in contact.php, member.php?action=do_resendactivation, member.php?action=do_lostpw, member.php?action=do_emailuser, and sendthread.php?action=do_sendtofriend do not call captcha::invalidate_captcha() for the MyBB Default CAPTCHA selected by the captchaimage setting. A valid response can therefore be reused until a non-vulnerable endpoint invalidates it, an incorrect response is submitted, or the challenge expires. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45734.json
- https://github.com/mybb/mybb/security/advisories/GHSA-jrrr-f3jw-mjmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45734
- https://github.com/mybb/mybb/commit/c2ed54f9259b9ce05728a9e657169033fe4adffc
