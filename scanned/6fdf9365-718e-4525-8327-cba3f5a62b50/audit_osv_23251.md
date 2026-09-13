# [H] Airtable.js credentials exposed in browser builds

## Summary
Severity: High
Advisory: CVE-2022-46155
Aliases: GHSA-vqm5-9546-x25v
CVSS: 7.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-11-29
Source: https://osv.dev/vulnerability/CVE-2022-46155
Type: osv

## Details
Airtable.js is the JavaScript client for Airtable. Prior to version 0.11.6, Airtable.js had a misconfigured build script in its source package. When the build script is run, it would bundle environment variables into the build target of a transpiled bundle. Specifically, the AIRTABLE_API_KEY and AIRTABLE_ENDPOINT_URL environment variables are inserted during Browserify builds due to being referenced in Airtable.js code. This only affects copies of Airtable.js built from its source, not those installed via npm or yarn. Airtable API keys set in users’ environments via the AIRTABLE_API_KEY environment variable may be bundled into local copies of Airtable.js source code if all of the following conditions are met: 1) the user has cloned the Airtable.js source onto their machine, 2) the user runs the `npm prepare` script, and 3) the user' has the AIRTABLE_API_KEY environment variable set. If these conditions are met, a user’s local build of Airtable.js would be modified to include the value of the AIRTABLE_API_KEY environment variable, which could then be accidentally shipped in the bundled code. Users who do not meet all three of these conditions are not impacted by this issue. Users should upgrade to Airtable.js version 0.11.6 or higher; or, as a workaround unset the AIRTABLE_API_KEY environment variable in their shell and/or remove it from your .bashrc, .zshrc, or other shell configuration files. Users should also regenerate any Airtable API keys they use, as the keysy may be present in bundled code.

## References
- https://github.com/Airtable/airtable.js/pull/330/commits/b468d8fe48d75e3d5fe46d0ea7770f4658951ed0
- https://github.com/Airtable/airtable.js/releases/tag/v0.11.6
- https://github.com/Airtable/airtable.js/security/advisories/GHSA-vqm5-9546-x25v
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46155.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46155
