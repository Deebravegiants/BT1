# [M] @dependencytrack/frontend vulnerable to Persistent Cross-Site-Scripting via welcome message

## Summary
Severity: Medium
Advisory: GHSA-7xvh-c266-cfr5
CVE: CVE-2025-64758
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-11-17
Source: https://github.com/advisories/GHSA-7xvh-c266-cfr5
Type: github-advisory

## Affected
- npm: `@dependencytrack/frontend` — affected >=4.12.0 <4.13.6

## Details
### Description

Since version 4.12.0, Dependency-Track users with the `SYSTEM_CONFIGURATION` permission can configure a "welcome message", which is HTML that is to be rendered on the login page for branding purposes.

When rendering the welcome message, Dependency-Track versions before 4.13.6 did not properly sanitize the HTML, allowing arbitrary JavaScript to be executed.

### Impact

Users with the `SYSTEM_CONFIGURATION` permission (i.e., administrators), can exploit this weakness to execute arbitrary JavaScript for users browsing to the login page. 

### Patches

The issue has been fixed in version 4.13.6.

### References

* The issue was introduced via: https://github.com/DependencyTrack/frontend/pull/986
* The issue was fixed via: https://github.com/DependencyTrack/frontend/pull/1378

### Credit

Thanks to *Jonas Benjamin Friedli* for identifying and responsibly disclosing the issue.

## References
- https://github.com/DependencyTrack/frontend/security/advisories/GHSA-7xvh-c266-cfr5
- https://nvd.nist.gov/vuln/detail/CVE-2025-64758
- https://github.com/DependencyTrack/frontend/pull/1378
- https://github.com/DependencyTrack/frontend/pull/986
- https://github.com/DependencyTrack/frontend/commit/8fd757be612eaf4f35eadbe4c334204d7bd711be
- https://github.com/DependencyTrack/frontend
