# [H] Apiman has potential permissions bypass

## Summary
Severity: High
Advisory: GHSA-j94p-hv25-rm5g
CVE: CVE-2022-47551
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-01-03
Source: https://github.com/advisories/GHSA-j94p-hv25-rm5g
Type: github-advisory

## Affected
- Maven: `io.apiman:apiman-manager-api-rest-impl` — affected >=1.5.7 <3.0.0.Final

## Details
### Impact

Incorrect default permissions for certain read-only resources in the Apiman 1.5.7.Final through 2.2.3.Final in the Apiman Manager REST API allows a remote authenticated attacker to access information and resources in an Apiman Organizations they are not a member of and/or do not have permissions for.

For example, an attacker may be able to craft an HTTP request to discover APIs that are private to organizations they are not members of, via fuzzing, search, and other similar mechanisms.

If the attacker has sufficient permissions in their own organization, they may also be able to sign up to the private APIs they have discovered by crafting a tailored HTTP request, thereby gaining access to an API Management protected resource that they should have access to.

* A malicious account-holder may be able to see information about APIs they do not have permission for.

* A malicious account-holder may be able to sign up to APIs they do not have permission for, and hence access API Management-protected resources they are not authorized to access.

* This does NOT relate to the Apiman Gateway.

### Patches

* Upgrade to Apiman 3.0.0.Final (or later). The issue is fixed in this version.

* If you are using an older version of Apiman, contact to your [Apiman support provider](https://www.apiman.io/support.html) for advice/long-term support.

### References

* https://www.apiman.io/blog/permissions-bypass-disclosure/
* https://github.com/advisories/GHSA-54r5-wr8x-x5v3
* https://nvd.nist.gov/vuln/detail/CVE-2022-47551
* https://github.com/orgs/apiman/discussions/2409

## References
- https://github.com/apiman/apiman/security/advisories/GHSA-j94p-hv25-rm5g
- https://nvd.nist.gov/vuln/detail/CVE-2022-47551
- https://github.com/advisories/GHSA-54r5-wr8x-x5v3
- https://github.com/apiman/apiman
- https://github.com/orgs/apiman/discussions/2409
- https://www.apiman.io/blog/permissions-bypass-disclosure
