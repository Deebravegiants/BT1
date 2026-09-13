# [M] Email addresses are not hidden regardless of selected state in mprweb

## Summary
Severity: Medium
Advisory: CVE-2022-31185
Aliases: GHSA-jm39-h693-678g
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/CVE-2022-31185
Type: osv

## Details
mprweb is a hosting platform for the makedeb Package Repository. Email addresses were found to not have been hidden, even if a user had clicked the `Hide Email Address` checkbox on their account page, or during signup. This could lead to an account's email being leaked, which may be problematic if your email needs to remain private for any reason. Users hosting their own mprweb instance will need to upgrade to the latest commit to get this fixed. Users on the official instance will already have this issue fixed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31185.json
- https://github.com/makedeb/mprweb/security/advisories/GHSA-jm39-h693-678g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31185
- https://github.com/makedeb/mprweb/commit/d13e3f2f5a9c0b0f6782f35d837090732026ad77
