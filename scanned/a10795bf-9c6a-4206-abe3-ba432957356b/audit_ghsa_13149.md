# [M] WireMock Controlled Server Side Request Forgery vulnerability through URL

## Summary
Severity: Medium
Advisory: GHSA-hq8w-9w8w-pmx7
CVE: CVE-2023-41327
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-hq8w-9w8w-pmx7
Type: github-advisory

## Affected
- Maven: `org.wiremock:wiremock-webhooks-extension` — affected >=3.0.0 <3.0.3
- Maven: `org.wiremock:wiremock-webhooks-extension` — affected >=2.0.0 <2.35.1

## Details
### Impact

WireMock can be configured to only permit proxying (and therefore recording) to certain addresses. This is achieved via a list of allowed address rules and a list of denied address rules, where the allowed list is evaluated first. [Documentation](https://wiremock.org/docs/configuration/#preventing-proxying-to-and-recording-from-specific-target-addresses). 

Until WireMock Webhooks Extension [3.0.0-beta-15](https://github.com/wiremock/wiremock/releases/tag/3.0.0-beta-15), the filtering of target addresses from the proxy mode DID NOT work for Webhooks, so the users were potentially vulnerable regardless of the `limitProxyTargets` settings. 

Via the WireMock webhooks configuration, POST requests from a webhook might be forwarded to an arbitrary service reachable from WireMock’s instance. For example, If someone is running the WireMock docker Container inside a private cluster, they can trigger internal POST requests against unsecured APIs or even against secure ones by passing a token, discovered using another exploit, via authentication headers.

### Affected  components

- WireMock Webhooks Extension 2.x versions until 2.35.1 (security patch)
- WireMock 3.x version until 3.0.3 (security patch)
- All versions of WireMock Studio (discontinued). This distribution bundles the WireMock Webhooks Extension and activates it by default

### Patches and Mitigation

- For WireMock 2.x and 3.x - upgrade to the versions with the security patches
- Setup network restrictions similarly to https://wiremock.org/docs/configuration/#preventing-proxying-to-and-recording-from-specific-target-addresses 
- For WireMock Studio: Stop using discontinued WireMock Studio, migrate to other distributions. The vendor of WireMock Studio recommends migration to [WireMock Cloud](https://www.wiremock.io/product)

NOTE: It was confirmed that [WireMock Cloud](https://www.wiremock.io/product) does not expose sensitive internal APIs and hence not vulnerable to the issue. No action is needed if you use this SaaS distribution.

### Workarounds

- Use external firewall rules to define the list of permitted destinations

### References

- CVE-2023-39967
- [Preventing proxying to and recording from specific target addresses](https://wiremock.org/docs/configuration/#preventing-proxying-to-and-recording-from-specific-target-addresses)

### Credits

- @W0rty for reporting CVE-2023-39967 in WireMock Studio
- WireMock Inc. team for discovering similar exploits in Webhooks and the risk in the Proxy mode defaults for WireMock

## References
- https://github.com/wiremock/wiremock/security/advisories/GHSA-hq8w-9w8w-pmx7
- https://nvd.nist.gov/vuln/detail/CVE-2023-41327
- https://github.com/wiremock/wiremock
- https://github.com/wiremock/wiremock/releases/tag/2.35.1
- https://github.com/wiremock/wiremock/releases/tag/3.0.0-beta-15
- https://github.com/wiremock/wiremock/releases/tag/3.0.3
- https://wiremock.org/docs/configuration/#preventing-proxying-to-and-recording-from-specific-target-addresses
