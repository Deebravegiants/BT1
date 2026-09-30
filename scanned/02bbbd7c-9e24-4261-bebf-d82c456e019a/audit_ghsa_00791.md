# [M] Validation Bypass in paypal-ipn

## Summary
Severity: Medium
Advisory: GHSA-h698-r4hm-w94p
CVE: CVE-2014-10067
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-h698-r4hm-w94p
Type: github-advisory

## Affected
- npm: `paypal-ipn` — affected >=0 <3.0.0

## Details
Versions 2.x.x and earlier of `paypal-ipn` are affected by a validation bypass vulnerability. 

paypal-ipn uses the `test_ipn` parameter (which is set by the PayPal IPN simulator) to determine if it should use the production PayPal site or the sandbox.

A motivated attacker could craft a request string using the simulator to fool the application into entering the sandbox mode, potentially allowing purchases without valid payment.


## Recommendation

Upgrade to version 3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10067
- https://github.com/andzdroid/paypal-ipn/issues/11
- https://github.com/andzdroid/paypal-ipn
- https://www.npmjs.com/advisories/26
