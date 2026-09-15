# [C] Session takeover vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-13602
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:U)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-13602
Type: osv

## Details
We found a chain of combining multiple weaknesses in the product that could allow an attacker to become any user in the backend and access any data:







  *  


The payment integration plugins Stripe (included in the core system), pretix-mollie, pretix-oppwa, pretix-bitpay, pretix-payone, pretix-secuconnect, pretix-sofort, and pretix-saferpay
 contain a code path that is intended for the transport of session 
parameters from a tab with isolated cookies (e.g. in the pretix widget) 
to a new tab. For this purpose, a set of session parameters is 
cryptographically signed and then passed to the new tab as a URL 
parameter. The plugins perform no further validation of the session 
parameters, other than the cryptographic signature being valid. This is 
fixed with the releases issued today by strictly validating that no 
session parameters outside of the scope of the respective plugin may be 
set.




  *  


An unrelated feature in the core system is used to generate redirect links that obfuscate any Referer
 headers for outgoing links to prevent leakage of secrets in URLs. This 
redirect page also requires cryptographically signed parameters. 
Unfortunately, it uses the same key and salt for the signature as the 
previously mentioned feature in the payment integration plugins. A 
motivated attacker with access to at least one event in the backend can 
trick the system into cryptographically signing arbitrary content using 
specially crafted links. In combination with the previous issue, the 
attacker could use this to set and modify arbitrary parameters on their 
user session by injecting the signed parameters into the feature of the 
payment providers. This is fixed with the releases issued today by using
 different salts for the signature for each plugin and feature.




  *  


A third, unrelated feature in the core system is used for admin users
 to act on behalf of another user, mostly for debugging purposes. With 
being able to insert arbitrary parameters into a session, an attacker 
can abuse this feature to change their session from their actual user to
 any user in the system by guessing a valid user ID. This is fixed with
 the release today by requiring unguessable information to be contained 
in the session of the user to switch to.

## References
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13602.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13602
- https://pretix.eu/about/en/blog/20260701-release-2026-5-3/
- https://github.com/pretix/pretix
- https://github.com/pretix/pretix-bitpay
- https://github.com/pretix/pretix-mollie
- https://github.com/pretix/pretix-oppwa
- https://github.com/pretix/pretix-payone
- https://github.com/pretix/pretix-saferpay
- https://github.com/pretix/pretix-secuconnect
- https://github.com/pretix/pretix-sofort
