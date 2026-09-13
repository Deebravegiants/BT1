# [M] CVE-2019-10741

## Summary
Severity: Medium
Advisory: CVE-2019-10741
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-04-07
Source: https://osv.dev/vulnerability/CVE-2019-10741
Type: osv

## Details
K-9 Mail v5.600 can include the original quoted HTML code of a specially crafted, benign looking, email within (digitally signed) reply messages. The quoted part can contain conditional statements that show completely different text if opened in a different email client. This can be abused by an attacker to obtain valid S/MIME or PGP signatures for arbitrary content to be displayed to a third party. NOTE: the vendor states "We don't plan to take any action because of this."

## References
- https://github.com/k9mail/k-9/issues/3925
