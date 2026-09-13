# [H] CSV Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-h7vq-5qgw-jwwq
CVE: CVE-2021-41824
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-18
Source: https://github.com/advisories/GHSA-h7vq-5qgw-jwwq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=3.4.0 <3.7.14

## Details
### Impact
In some circumstances, it was possible to export data in CSV format that could trigger a payload in old versions of Excel.

If you are accepting user input from untrusted sources and will be exporting that data in CSV format from element index pages and there is a chance users will open that on old versions of Excel, then you should update.

### Patches
This has been patched in Craft 3.7.14.

### References
* https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#3714---2021-09-28
* https://twitter.com/craftcmsupdates/status/1442928690145366018

### For more information

If you have any questions or comments about this advisory, email us at support@craftcms.com

----------

Credits: BAE Systems AI Vulnerability Research Team – Azrul Ikhwan Zulkifli

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-h7vq-5qgw-jwwq
- https://nvd.nist.gov/vuln/detail/CVE-2021-41824
- https://github.com/craftcms/cms/commit/c9cb2225f1b908fb1e8401d401219228634b26b2
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#3714---2021-09-28
- https://twitter.com/craftcmsupdates/status/1442928690145366018
