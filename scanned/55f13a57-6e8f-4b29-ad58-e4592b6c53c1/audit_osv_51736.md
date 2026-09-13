# [M] CVE-2021-38502

## Summary
Severity: Medium
Advisory: CVE-2021-38502
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-38502
Type: osv

## Details
Thunderbird ignored the configuration to require STARTTLS security for an SMTP connection. A MITM could perform a downgrade attack to intercept transmitted messages, or could take control of the authenticated session to execute SMTP commands chosen by the MITM. If an unprotected authentication method was configured, the MITM could obtain the authentication credentials, too. This vulnerability affects Thunderbird < 91.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-47/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1733366
- https://www.debian.org/security/2022/dsa-5034
