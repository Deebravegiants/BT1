# [H] Code injection in Stripe CLI on windows

## Summary
Severity: High
Advisory: GHSA-4cx6-fj7j-pjx9
CVE: CVE-2022-24753
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-4cx6-fj7j-pjx9
Type: github-advisory

## Affected
- Go: `github.com/stripe/stripe-cli` — affected >=0 <1.7.13

## Details
### Impact
A vulnerability in Stripe CLI exists on Windows when certain commands are run in a directory where an attacker has planted files. The commands are `stripe login`, `stripe config -e`, `stripe community`, and `stripe open`. MacOS and Linux are unaffected.

An attacker who successfully exploits the vulnerability can run arbitrary code in the context of the current user. The update addresses the vulnerability by throwing an error in these situations before the code can run.

There has been no evidence of exploitation of this vulnerability.

### Recommendation
Upgrade to Stripe CLI v1.7.13.

### Acknowledgments
Thanks to [trungpabc](https://hackerone.com/trungpabc) for reporting the issue.

### For more information
Email us at [security@stripe.com](mailto:security@stripe.com).

## References
- https://github.com/stripe/stripe-cli/security/advisories/GHSA-4cx6-fj7j-pjx9
- https://nvd.nist.gov/vuln/detail/CVE-2022-24753
- https://github.com/stripe/stripe-cli/commit/be38da5c0191adb77f661f769ffff2fbc7ddf6cd
- https://github.com/stripe/stripe-cli
