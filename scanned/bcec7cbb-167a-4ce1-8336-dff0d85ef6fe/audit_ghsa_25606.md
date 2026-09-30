# [M] Phoenix Arbitrary URL Redirect

## Summary
Severity: Medium
Advisory: GHSA-cmfh-8f8r-fj96
CVE: CVE-2017-1000163
CWE: CWE-601
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-cmfh-8f8r-fj96
Type: github-advisory

## Affected
- Hex: `phoenix` — affected >=0 <1.0.6
- Hex: `phoenix` — affected >=1.1.0 <1.1.8
- Hex: `phoenix` — affected >=1.2.0 <1.2.3

## Details
The Phoenix team designed `Phoenix.Controller.redirect/2` to protect against redirects allowing user input to redirect to an external URL where your application code otherwise assumes a local path redirect. This is why the `:to` option is used for “local” URL redirects and why you must pass the `:external` option to intentionally allow external URLs to be redirected to. It has been disclosed that carefully crafted user input may be treated by some browsers as an external URL. An attacker can use this vulnerability to aid in social engineering attacks. The most common use would be to create highly believable phishing attacks. For example, the following user input would pass local URL validation, but be treated by Chrome and Firefox as external URLs: 
`http://localhost:4000/?redirect=/\nexample.com`
Not all browsers are affected, but latest Chrome and Firefox will issue a get request for `example.com` and successfully redirect externally

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000163
- https://elixirforum.com/t/security-releases-for-phoenix/4143
- https://github.com/phoenixframework/phoenix
