# [M] Comment reply notifications sent to incorrect users

## Summary
Severity: Medium
Advisory: GHSA-xqxm-2rpm-3889
CVE: CVE-2022-21683
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-xqxm-2rpm-3889
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=2.13 <2.15.2

## Details
### Impact
When notifications for new replies in comment threads are sent, they are sent to all users who have replied or commented anywhere on the site, rather than only in the relevant threads. This means that a user could listen in to new comment replies on pages they have not had editing access to, as long as they have left a comment or reply somewhere on the site.

### Patches
A patched version has been released as Wagtail 2.15.2 (for the current LTS), which restores the intended behaviour - to send notifications for new replies to the participants in the active thread only (editing permissions are not considered).

### Workarounds
New comments can be disabled by setting `WAGTAILADMIN_COMMENTS_ENABLED = False` in the Django settings file.

### Acknowledgements

Many thanks to Ihor Marhitych for identifying this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at security@wagtail.io (if you wish to send encrypted email, the public key ID is `0x6ba1e1a86e0f8ce8`)

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-xqxm-2rpm-3889
- https://nvd.nist.gov/vuln/detail/CVE-2022-21683
- https://github.com/wagtail/wagtail/commit/5fe901e5d86ed02dbbb63039a897582951266afd
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2022-13.yaml
- https://github.com/wagtail/wagtail
- https://github.com/wagtail/wagtail/releases/tag/v2.15.2
