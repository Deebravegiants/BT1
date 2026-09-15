# [M] Apiman vulnerable to permissions bypass due to missing check on API key URL

## Summary
Severity: Medium
Advisory: GHSA-m6f8-hjrv-mw5f
CVE: CVE-2023-28640
CWE: CWE-269, CWE-280, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-m6f8-hjrv-mw5f
Type: github-advisory

## Affected
- Maven: `io.apiman:apiman-manager-api-rest-impl` — affected >=0 <3.1.0.Final

## Details
### Impact

Due to a missing permissions check, an attacker with an authenticated Apiman Manager account may be able to gain access to API keys they do not have permission for if they correctly guess the URL. The URL includes Organisation ID, Client ID, and Client Version of the targeted non-permitted resource, and each of these can have arbitrary values.

While not trivial to exploit, it could be achieved by brute-forcing or guessing common names.

Access to the non-permitted API Keys could allow use of other users' resources without their permission (depending on the specifics of configuration, such as whether an API key is the only form of security).

### Patches

Apiman 3.1.0.Final and later resolves this issue. 

### Workarounds

Only provide Apiman Manager accounts to known users, do not allow anonymous/unknown users to create an Apiman Manager account.

Note that this does **not** affect the Apiman Gateway.

### References

* [Blog post disclosing issue](https://www.apiman.io/blog/potential-permissions-bypass-disclosure/)

## References
- https://github.com/apiman/apiman/security/advisories/GHSA-m6f8-hjrv-mw5f
- https://nvd.nist.gov/vuln/detail/CVE-2023-28640
- https://github.com/apiman/apiman
- https://www.apiman.io/blog/potential-permissions-bypass-disclosure
