# [M] Cross-Site Scripting in BookStack

## Summary
Severity: Medium
Advisory: GHSA-5vf7-q87h-pg6w
CVE: CVE-2020-11055
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-05-07
Source: https://github.com/advisories/GHSA-5vf7-q87h-pg6w
Type: github-advisory

## Affected
- Packagist: `ssddanbrown/bookstack` — affected >=0.18.0 <0.29.2

## Details
### Impact

A user with permission to create comments could POST HTML directly to the system to be saved in a comment, which would then be executed/displayed to others users viewing the comment. Through this vulnerability custom JavaScript code could be injected and therefore ran on other user machines.

This most impacts scenarios where not-trusted users are given permission to create comments.

### Patches

The issue was addressed in BookStack v0.29.2.

After upgrading, The command `php artisan bookstack:regenerate-comment-content` should be ran to remove any pre-existing dangerous content. 

### Workarounds

Comments can be disabled in the system settings to prevent them being shown to users. Alternatively, comment creation permissions can be altered as required to only those who are trusted but this will not address existing exploitation of this vulnerability. 

### References

* [BookStack Beta v0.29.2](https://github.com/BookStackApp/BookStack/releases/tag/v0.29.2)
* JVN#41035278
* [BookStack Blog Post](https://bookstackapp.com/blog/beta-release-v0-29-2/)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [the BookStack GitHub repository](BookStackApp/BookStack/issues).
* Ask on the [BookStack Discord chat](https://discord.gg/ztkBqR2).
* Follow the [BookStack Security Advice](https://github.com/BookStackApp/BookStack#-security) to contact someone privately.

## References
- https://github.com/BookStackApp/BookStack/security/advisories/GHSA-5vf7-q87h-pg6w
- https://nvd.nist.gov/vuln/detail/CVE-2020-11055
- https://bookstackapp.com/blog/beta-release-v0-29-2
- https://github.com/BookStackApp/BookStack/releases/tag/v0.29.2
- http://jvn.jp/en/jp/JVN41035278/index.html
