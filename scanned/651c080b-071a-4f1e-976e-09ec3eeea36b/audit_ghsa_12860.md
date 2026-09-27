# [M] Apiman Manager API affected by Jackson denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q95j-488q-5q3p
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-q95j-488q-5q3p
Type: github-advisory

## Affected
- Maven: `io.apiman:apiman-manager-api-impl` — affected >=0 <3.0.0.Final

## Details
### Impact

Due to a vulnerability in `jackson-databind <= 2.12.6.0`, an authenticated attacker could craft an Apiman policy configuration which, when saved, may cause a denial of service on the Apiman Manager API.

This does **not** affect the Apiman Gateway.

### Patches

Upgrade to Apiman 3.0.0.Final or later.

If you are using an older version of Apiman and need to remain on that version, contact your Apiman [support provider](https://www.apiman.io/support.html) for advice/long-term support.

### Workarounds

If all users of the Apiman Manager are trusted then you may assess this is low risk, as an account is required to exploit the vulnerability.

### References

* Apiman maintainer and security contact: marc@blackparrotlabs.io
* https://nvd.nist.gov/vuln/detail/CVE-2020-36518
* https://github.com/FasterXML/jackson-databind/issues/2816

## References
- https://github.com/apiman/apiman/security/advisories/GHSA-q95j-488q-5q3p
- https://nvd.nist.gov/vuln/detail/CVE-2020-36518
- https://github.com/FasterXML/jackson-databind/issues/2816
- https://github.com/apiman/apiman
