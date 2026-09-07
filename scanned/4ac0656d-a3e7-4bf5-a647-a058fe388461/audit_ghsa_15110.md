# [M] readthedocs-sphinx-search vulnerable to cross-site scripting when including search results from malicious projects

## Summary
Severity: Medium
Advisory: GHSA-xgfm-fjx6-62mj
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-01-16
Source: https://github.com/advisories/GHSA-xgfm-fjx6-62mj
Type: github-advisory

## Affected
- PyPI: `readthedocs-sphinx-search` — affected >=0 <0.3.2

## Details
### Impact

This vulnerability could have allowed an attacker to include arbitrary HTML content in search results by having a user search a malicious project. This was due to our search client not correctly escaping all user content from search results. You can find more information in the [advisory published in our readthedocs.org repo](https://github.com/readthedocs/readthedocs.org/security/advisories/GHSA-qhqx-5j25-rv48).

Users of this extension should update to the 0.3.2 version, and trigger a new build.

This issue was discovered by a member of our team, and we have seen no signs that this vulnerability was exploited in the wild.

### Patches

This issue has been patched in our 0.3.2 version. 

### References

- https://github.com/readthedocs/readthedocs-sphinx-search/commit/8c6f6d01e88e72ef32ed0c220b6c19d1e1121c73

### For more information

If you have any questions or comments about this advisory, email us at [security@readthedocs.org](mailto:security@readthedocs.org) ([PGP](https://docs.readthedocs.io/page/security.html#pgp-key))

## References
- https://github.com/readthedocs/readthedocs-sphinx-search/security/advisories/GHSA-xgfm-fjx6-62mj
- https://github.com/readthedocs/readthedocs-sphinx-search/commit/8c6f6d01e88e72ef32ed0c220b6c19d1e1121c73
- https://github.com/readthedocs/readthedocs-sphinx-search
