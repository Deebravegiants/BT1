# [H] Uncontrolled Resource Consumption in @discordjs/opus

## Summary
Severity: High
Advisory: GHSA-rvgf-69j7-xh78
CVE: CVE-2022-25345
CWE: CWE-908
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-rvgf-69j7-xh78
Type: github-advisory

## Affected
- npm: `@discordjs/opus` — affected >=0 <0.8.0

## Details
Improperly handled errors in @discordjs/opus cause hard crashes instead of returning the error to user land. All versions of package @discordjs/opus (<= 0.7.0) are vulnerable to Denial of Service (DoS) when trying to encode using an encoder with zero channels, or a non-initialized buffer. This leads to a hard crash due to improperly returning the errors from the invalid inputs.

As of version 0.8.0, the errors are correctly returned to the user and are no longer throwing hard crashes that cannot be recovered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25345
- https://github.com/discordjs/opus/commit/406249f3fca484a2af97a34ceb989019efa09bc7
- https://github.com/discordjs/opus
- https://github.com/discordjs/opus/blob/3ca4341ffdd81cf83cec57045e59e228e6017590/src/node-opus.cc#L28
- https://github.com/discordjs/opus/releases/tag/v0.8.0
- https://snyk.io/vuln/SNYK-JS-DISCORDJSOPUS-2403100
