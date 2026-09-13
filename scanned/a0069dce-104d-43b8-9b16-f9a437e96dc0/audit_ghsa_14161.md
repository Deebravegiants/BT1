# [M] Buffer under-read in workerd

## Summary
Severity: Medium
Advisory: GHSA-8vx6-69vg-c46f
CVE: CVE-2023-2512
CWE: CWE-125, CWE-127, CWE-190
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-8vx6-69vg-c46f
Type: github-advisory

## Affected
- npm: `workerd` — affected >=0 <1.20230419.0

## Details
### Impact
Prior to version v1.20230419.0, the FormData API implementation was subject to an integer overflow. If a FormData instance contained more than 2^31 elements, the `forEach()` method could end up reading from the wrong location in memory while iterating over elements. This would most likely lead to a segmentation fault, but could theoretically allow arbitrary undefined behavior.

In order for the bug to be exploitable, the process would need to be able to allocate 160GB of RAM. Due to this, the bug was never exploitable on the Cloudflare Workers platform, but could theoretically be exploitable on deployments of workerd running on machines with a huge amount of memory. Moreover, in order to be remotely exploited, an attacker would have to upload a single form-encoded HTTP request of at least tens of gigabytes in size. The application code would then have to use `request.formData()` to parse the request and `formData.forEach()` to iterate over this data. Due to these limitations, the exploitation likelihood was considered Low.

### Patches
A fix that addresses this vulnerability has been released in version v1.20230419.0 and users are encouraged to update to the latest version available.

### References
Release - https://github.com/cloudflare/workerd/releases/tag/v1.20230419.0

## References
- https://github.com/cloudflare/workerd/security/advisories/GHSA-8vx6-69vg-c46f
- https://nvd.nist.gov/vuln/detail/CVE-2023-2512
- https://github.com/cloudflare/workerd
- https://github.com/cloudflare/workerd/releases/tag/v1.20230419.0
