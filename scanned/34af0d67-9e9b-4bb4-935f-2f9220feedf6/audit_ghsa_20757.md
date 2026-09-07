# [M] Unbounded resource exhaustion in cmark-gfm autolink extension may lead to denial of service

## Summary
Severity: Medium
Advisory: GHSA-4qw4-jpp4-8gvp
CWE: CWE-400
Ecosystem: RubyGems
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-4qw4-jpp4-8gvp
Type: github-advisory

## Affected
- RubyGems: `commonmarker` — affected >=0 <0.23.6

## Details
### Impact

CommonMarker uses `cmark-gfm` for rendering [Github Flavored Markdown](https://github.github.com/gfm/). A polynomial time complexity issue in cmark-gfm's autolink extension may lead to unbounded resource exhaustion and subsequent denial of service.

### Patches

This vulnerability has been patched in the following CommonMarker release:

- v0.23.6

### Workarounds

Disable use of the autolink extension.

### References

https://github.com/gjtorikian/commonmarker/pull/190
https://github.com/github/cmark-gfm/security/advisories/GHSA-cgh3-p57x-9q7q
https://en.wikipedia.org/wiki/Time_complexity

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github/cmark-gfm](https://github.com/github/cmark-gfm)

### Acknowledgements

We would like to thank [Legit Security](https://www.legitsecurity.com) for reporting this vulnerability.

## References
- https://github.com/gjtorikian/commonmarker/security/advisories/GHSA-4qw4-jpp4-8gvp
- https://github.com/gjtorikian/commonmarker/pull/190
- https://github.com/gjtorikian/commonmarker
- https://github.com/gjtorikian/commonmarker/releases/tag/v0.23.6
