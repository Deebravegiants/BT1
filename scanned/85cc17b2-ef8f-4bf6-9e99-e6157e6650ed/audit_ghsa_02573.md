# [M] Prototype Pollution in the merge and clone helper methods

## Summary
Severity: Medium
Advisory: GHSA-fhv8-fx5f-7fxf
CVE: CVE-2021-39227
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-fhv8-fx5f-7fxf
Type: github-advisory

## Affected
- npm: `zrender` — affected >=5.0.0 <5.2.1
- npm: `zrender` — affected >=0 <4.3.3

## Details
### Impact
Using `merge` and `clone` helper methods in the `src/core/util.ts` module will have prototype pollution. It will affect the popular data visualization library Apache ECharts, which is using and exported these two methods directly.

### Patches
 
It has been patched in https://github.com/ecomfe/zrender/pull/826. 
Users should update zrender to `5.2.1`.  and update echarts to `5.2.1` if project is using echarts.

### References
NA

### For more information
NA

## References
- https://github.com/ecomfe/zrender/security/advisories/GHSA-fhv8-fx5f-7fxf
- https://nvd.nist.gov/vuln/detail/CVE-2021-39227
- https://github.com/ecomfe/zrender/pull/826
- https://github.com/ecomfe/zrender
- https://github.com/ecomfe/zrender/releases/tag/5.2.1
