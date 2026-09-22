# [H] Unsanitized JavaScript code injection possible in gatsby-plugin-mdx

## Summary
Severity: High
Advisory: GHSA-mj46-r4gr-5x83
CVE: CVE-2022-25863
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-mj46-r4gr-5x83
Type: github-advisory

## Affected
- npm: `gatsby-plugin-mdx` — affected >=0 <2.14.1
- npm: `gatsby-plugin-mdx` — affected >=3.0.0 <3.15.2

## Details
### Impact
The gatsby-plugin-mdx plugin prior to versions 3.15.2 and 2.14.1 passes input through to the `gray-matter` npm package, which is vulnerable to JavaScript injection in its default configuration, unless input is sanitized.  The vulnerability is present when passing input in both webpack (MDX files in `src/pages` or MDX file imported as component in frontend / React code) and data mode (querying MDX nodes via GraphQL).  Injected JavaScript executes in the context of the build server.

To exploit this vulnerability untrusted/unsanitized input would need to be sourced or added into an MDX file.  The following MDX payload demonstrates a vulnerable configuration:
```
---js
((require("child_process")).execSync("id >> /tmp/rce"))
--- 
```

### Patches
A patch has been introduced in `gatsby-plugin-mdx@3.15.2` and `gatsby-plugin-mdx@2.14.1` which mitigates the issue by disabling the `gray-matter` JavaScript Frontmatter engine.  The patch introduces a new option, `JSFrontmatterEngine` which is set to `false` by default.  When setting `JSFrontmatterEngine` to `true`, input passed to `gatsby-plugin-mdx` must be sanitized before processing to avoid a security risk.  Warnings are displayed when enabling `JSFrontmatterEngine` to `true` or if it appears that the MDX input is attempting to use the Frontmatter engine.

### Workarounds
If an older version of `gatsby-plugin-mdx` must be used, input passed into the plugin should be sanitized ahead of processing.

**We encourage projects to upgrade to the latest major release branch for all Gatsby plugins to ensure the latest security updates and bug fixes are received in a timely manner.**

### Credits
We would like to thank Snyk [snyk.io] for initially bringing the issue to our attention, as well as Feng Xiao and Zhongfu Su, who reported the issue to Snyk.

### For more information
Email us at [security@gatsbyjs.com](mailto:security@gatsbyjs.com).

## References
- https://github.com/gatsbyjs/gatsby/security/advisories/GHSA-mj46-r4gr-5x83
- https://nvd.nist.gov/vuln/detail/CVE-2022-25863
- https://github.com/gatsbyjs/gatsby/pull/35830
- https://github.com/gatsbyjs/gatsby/pull/35830/commits/f214eb0694c61e348b2751cecd1aace2046bc46e
- https://drive.google.com/file/d/1EoCzbwTWOM8-fjvwMbH3bqcZ2iKksxTW/view?usp=sharing
- https://github.com/gatsbyjs/gatsby
- https://snyk.io/vuln/SNYK-JS-GATSBYPLUGINMDX-2405699
