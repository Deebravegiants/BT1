# [H] gatsby-transformer-remark has possible unsanitized JavaScript code injection

## Summary
Severity: High
Advisory: GHSA-7ch4-rr99-cqcw
CVE: CVE-2023-22491
CWE: CWE-20, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-7ch4-rr99-cqcw
Type: github-advisory

## Affected
- npm: `gatsby-transformer-remark` — affected >=6.0.0 <6.3.2
- npm: `gatsby-transformer-remark` — affected >=0 <5.25.1

## Details
### Impact
The gatsby-transformer-remark plugin prior to versions 5.25.1 and 6.3.2 passes input through to the `gray-matter` npm package, which is vulnerable to JavaScript injection in its default configuration, unless input is sanitized.  The vulnerability is present in gatsby-transformer-remark when passing input in data mode (querying MarkdownRemark nodes via GraphQL).  Injected JavaScript executes in the context of the build server.

To exploit this vulnerability untrusted/unsanitized input would need to be sourced by or added into a file processed by gatsby-transformer-remark.  The following payload demonstrates a vulnerable configuration:
```
---js
((require("child_process")).execSync("id >> /tmp/rce"))
--- 
```

### Patches
A patch has been introduced in `gatsby-transformer-remark@5.25.1` and `gatsby-transformer-remark@6.3.2` which mitigates the issue by disabling the `gray-matter` JavaScript Frontmatter engine.  The patch introduces a new option, `JSFrontmatterEngine` which is set to `false` by default.  When setting `JSFrontmatterEngine` to `true`, input passed to `gatsby-plugin-mdx` must be sanitized before processing to avoid a security risk.  Warnings are displayed when enabling `JSFrontmatterEngine` to `true` or if it appears that the MarkdownRemark input is attempting to use the Frontmatter engine.

### Workarounds
If an older version of `gatsby-transformer-remark` must be used, input passed into the plugin should be sanitized ahead of processing.

**We encourage projects to upgrade to the latest major release branch for all Gatsby plugins to ensure the latest security updates and bug fixes are received in a timely manner.**


### For more information
Email us at [security@gatsbyjs.com](mailto:security@gatsbyjs.com).

## References
- https://github.com/gatsbyjs/gatsby/security/advisories/GHSA-7ch4-rr99-cqcw
- https://nvd.nist.gov/vuln/detail/CVE-2023-22491
- https://github.com/gatsbyjs/gatsby
