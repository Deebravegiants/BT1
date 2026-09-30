# [M] CVE-2021-32763

## Summary
Severity: Medium
Advisory: CVE-2021-32763
Aliases: GHSA-qqvp-j6gm-q56f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-32763
Type: osv

## Details
OpenProject is open-source, web-based project management software. In versions prior to 11.3.3, the `MessagesController` class of OpenProject has a `quote` method that implements the logic behind the Quote button in the discussion forums, and it uses a regex to strip `<pre>` tags from the message being quoted. The `(.|\s)` part can match a space character in two ways, so an unterminated `<pre>` tag containing `n` spaces causes Ruby's regex engine to backtrack to try 2<sup>n</sup> states in the NFA. This will result in a Regular Expression Denial of Service. The issue is fixed in OpenProject 11.3.3. As a workaround, one may install the patch manually.

## References
- https://github.com/opf/openproject/pull/9447.patch
- https://github.com/opf/openproject/security/advisories/GHSA-qqvp-j6gm-q56f
