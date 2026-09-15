# [M] lakeFS vulnerable to Arbitrary JavaScript Injection via Direct Link to HTML Files

## Summary
Severity: Medium
Advisory: GHSA-9phh-r37v-34wh
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-9phh-r37v-34wh
Type: github-advisory

## Affected
- Go: `github.com/treeverse/lakefs` — affected >=0 <0.106.0

## Details
### Impact
The browser renders the resulting HTML when opening a direct link to an HTML file via lakeFS. Any JavaScript within that page is executed within the context of the domain lakeFS is running in.  
An attacker can inject a malicious script inline, download resources from another domain, or make arbitrary HTTP requests. This would allow the attacker to send information to a random domain or carry out lakeFS operations while impersonating the victim.  

Note that to carry out this attack, an attacker must already have access to upload the malicious HTML file to one or more repositories. It also depends on the victim receiving and opening the link to the malicious HTML file.

### Patches
This is fixed in lakeFS version 0.106.0

### Workarounds
There are no known workarounds at this time.

## References
- https://github.com/treeverse/lakeFS/security/advisories/GHSA-9phh-r37v-34wh
- https://github.com/treeverse/lakeFS/commit/2b2a9fa156ad80b0aac043e17533b546b1800603
- https://github.com/treeverse/lakeFS
- https://github.com/treeverse/lakeFS/releases/tag/v0.106.0
