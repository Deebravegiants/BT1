# [M] Navigate endpoint is vulnerable to regex injection that may lead to Denial of Service.

## Summary
Severity: Medium
Advisory: GHSA-hf44-3mx6-vhhw
CVE: CVE-2021-29506
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-19
Source: https://github.com/advisories/GHSA-hf44-3mx6-vhhw
Type: github-advisory

## Affected
- Maven: `com.graphhopper:graphhopper-nav` — affected >=0 <2.4

## Details
### Impact
The regex injection that may lead to Denial of Service.

### Patches
Will be patched in 2.4 and 3.0

### Workarounds
Versions lower than 2.x are only affected if the navigation module is added

### References
See this pull request for the fix: https://github.com/graphhopper/graphhopper/pull/2304

If you have any questions or comments about this advisory please [send us an Email](https://www.graphhopper.com/contact-form/) or create a topic [here](https://discuss.graphhopper.com/).

## References
- https://github.com/graphhopper/graphhopper/security/advisories/GHSA-hf44-3mx6-vhhw
- https://nvd.nist.gov/vuln/detail/CVE-2021-29506
- https://github.com/graphhopper/graphhopper/pull/2304
- https://github.com/graphhopper/graphhopper/commit/eb189be1fa7443ebf4ae881e737a18f818c95f41
