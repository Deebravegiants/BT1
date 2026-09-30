# [H] Flarum post mentions can be used to read any post on the forum without access control

## Summary
Severity: High
Advisory: GHSA-22m9-m3ww-53h3
CVE: CVE-2023-22487
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-22m9-m3ww-53h3
Type: github-advisory

## Affected
- Packagist: `flarum/mentions` — affected >=0 <1.6.3

## Details
Using the mentions feature provided by the flarum/mentions extension, users can mention any post ID on the forum with the special `@"<username>"#p<id>` syntax.

The following behavior never changes no matter if the actor should be able to read the mentioned post or not:

A URL to the mentioned post is inserted into the actor post HTML, leaking its discussion ID and post number.

The `mentionsPosts` relationship included in the `POST /api/posts` and `PATCH /api/posts/<id>` JSON responses leaks the full JSON:API payload of all mentioned posts without any access control. This includes the content, date, number and attributes added by other extensions.

An attacker only needs the ability to create new posts on the forum to exploit the vulnerability. This works even if new posts require approval. If they have the ability to edit posts, the attack can be performed even more discreetly by using a single post to scan any size of database and hiding the attack post content afterward.

### Impact
The attack allows the leaking of all posts in the forum database, including posts awaiting approval, posts in tags the user has no access to, and private discussions created by other extensions like FriendsOfFlarum Byobu. This also includes non-comment posts like tag changes or renaming events. 

The discussion payload is not leaked but using the mention HTML payload it's possible to extract the discussion ID of all posts and combine all posts back together into their original discussions even if the discussion title remains unknown.

All Flarum versions prior to `v1.6.3` are affected.

### Patches
The vulnerability has been fixed and published as flarum/core v1.6.3. All communities running Flarum have to upgrade as soon as possible to v1.6.3 using:

```
composer update --prefer-dist --no-dev -a -W
```
You can then confirm you run the latest version using:

```
composer show flarum/core
```

### Workarounds
Disable the mentions extension.

### For more information
For any questions or comments on this vulnerability please visit https://discuss.flarum.org/

For support questions create a discussion at https://discuss.flarum.org/t/support.

A reminder that if you ever become aware of a security issue in Flarum, please report it to us privately by emailing [security@flarum.org](mailto:security@flarum.org), and we will address it promptly.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-22m9-m3ww-53h3
- https://nvd.nist.gov/vuln/detail/CVE-2023-22487
- https://github.com/flarum/framework/commit/ab1c868b978e8b0d09a5d682c54665dae17d0985
- https://github.com/flarum/framework
- https://github.com/flarum/framework/releases/tag/v1.6.3
