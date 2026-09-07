# [M] @dependencytrack/frontend vulnerable to  Persistent Cross-Site-Scripting via Vulnerability Details

## Summary
Severity: Medium
Advisory: GHSA-c33w-pm52-mqvf
CVE: CVE-2022-39350
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-c33w-pm52-mqvf
Type: github-advisory

## Affected
- npm: `@dependencytrack/frontend` — affected >=0 <4.6.1

## Details
### Description

Due to the common practice of providing vulnerability details in markdown format, the Dependency-Track frontend renders them using the JavaScript library [Showdown](https://github.com/showdownjs/showdown). Showdown [does not have any XSS countermeasures built in](https://github.com/showdownjs/showdown/wiki/Markdown's-XSS-Vulnerability-(and-how-to-mitigate-it)), and versions before 4.6.1 of the Dependency-Track frontend did not encode or sanitize Showdown's output. This made it possible for arbitrary JavaScript included in vulnerability details via HTML attributes to be executed in context of the frontend.

### Impact

Actors with the `VULNERABILITY_MANAGEMENT` permission can exploit this weakness by creating or editing a custom vulnerability and providing XSS payloads in any of the following fields:

* Description
* Details
* Recommendation
* References

The payload will be executed for users with the `VIEW_PORTFOLIO` permission when browsing to the modified vulnerability's page, for example: 

```
https://dtrack.example.com/vulnerabilities/INTERNAL/INT-jd8u-e8tl-8lwu
```

Alternatively, malicious JavaScript could be introduced via any of the vulnerability databases mirrored by Dependency-Track (NVD, GitHub Advisories, OSV, OSS Index, VulnDB). However, this attack vector is highly unlikely, and the team is not aware of any occurrence of this happening.

> **Note**
> The *Vulnerability Details* element of the *Audit Vulnerabilities* tab in the project view is **not** affected.

### Patches

The issue has been fixed in frontend version 4.6.1.

### Credit

Thanks to GitHub user **Waterstraal** for finding and responsibly disclosing the issue.

## References
- https://github.com/DependencyTrack/frontend/security/advisories/GHSA-c33w-pm52-mqvf
- https://nvd.nist.gov/vuln/detail/CVE-2022-39350
- https://docs.dependencytrack.org/changelog
- https://github.com/DependencyTrack/frontend
- https://github.com/showdownjs/showdown/wiki/Markdown's-XSS-Vulnerability-(and-how-to-mitigate-it)
