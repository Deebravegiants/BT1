# [H] CVE-2017-7981

## Summary
Severity: High
Advisory: CVE-2017-7981
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-29
Source: https://osv.dev/vulnerability/CVE-2017-7981
Type: osv

## Details
Tuleap before 9.7 allows command injection via the PhpWiki 1.3.10 SyntaxHighlighter plugin. This occurs in the Project Wiki component because the proc_open PHP function is used within PhpWiki before 1.5.5 with a syntax value in its first argument, and an authenticated Tuleap user can control this value, even with shell metacharacters, as demonstrated by a '<?plugin SyntaxHighlighter syntax="c;id"' line to execute the id command.

## References
- https://tuleap.net/file/shownotes.php?release_id=137#/linked-artifacts
- https://www.exploit-db.com/exploits/41953/
- https://tuleap.net/plugins/tracker/?aid=10159
- https://github.com/xdrr/vulnerability-research/blob/master/webapp/tuleap/2017.04.tuleap-auth-ci.md
