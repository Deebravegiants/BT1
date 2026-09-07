# [M] Use of insecure jQuery version in OctoberCMS

## Summary
Severity: Medium
Advisory: GHSA-v73w-r9xg-7cr9
Ecosystem: Packagist
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-v73w-r9xg-7cr9
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=1.0.319 <1.0.466
- Packagist: `october/system` — affected >=1.0.319 <1.0.466

## Details
### Impact
Passing HTML from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code.

### Patches
Issue has been patched in Build 466 (v1.0.466) by applying the recommended patch from @jquery.

### Workarounds
Apply https://github.com/octobercms/october/commit/5c7ba9fbe9f2b596b2f0e3436ee06b91b97e5892 to your installation manually if unable to upgrade to Build 466.

### References
- https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-11022
- https://jquery.com/upgrade-guide/3.5/

### For more information
If you have any questions or comments about this advisory:
* Email us at [octobercms@luketowers.ca](mailto:octobercms@luketowers.ca) & [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat Assessment
Assessed as Moderate by the @jquery team.

### Acknowledgements

Thanks to @mrgswift for reporting the issue to the October CMS team.

## References
- https://github.com/octobercms/october/security/advisories/GHSA-v73w-r9xg-7cr9
- https://github.com/octobercms/october/issues/5097
- https://github.com/octobercms/october/commit/5c7ba9fbe9f2b596b2f0e3436ee06b91b97e5892
- https://github.com/octobercms/october
