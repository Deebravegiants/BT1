# [C] qui CORS Misconfiguration: Arbitrary Origins Trusted

## Summary
Severity: Critical
Advisory: GHSA-h8vw-ph9r-xpch
CVE: CVE-2026-30924
CWE: CWE-942
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-h8vw-ph9r-xpch
Type: github-advisory

## Affected
- Go: `github.com/autobrr/qui` — affected >=0 <1.15.0

## Details
### Summary
The application implements an HTML5 cross-origin resource sharing (CORS) policy that allows access from any domain.

While the application is typically deployed within a trusted local network, successful exploitation of this weakness does not require any direct access to the instance by the attacker. Exploitation of this vulnerability uses the victim's browser as a conduit for interaction with the application.

The mechanism used is a malicious webpage that requests from or posts to sensitive application paths upon load. This may be made transparent to the user, and harvested data may be sent back to the attacker upon success.

### Cause and Remedy

```
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://example.com
```
The above response headers are responsible for the vulnerability. `Access-Control-Allow-Origin` was found to reflect arbitrary origins, implementing an effective blanket whitelist. Additionally, `Access-Control-Allow-Credentials` was returned as `true`, indicating to the browser that the loaded resource was permitted to leverage saved session information.

Correction of these values remediate the vulnerability. Defaulting to deny, with the configuration option to revert, should have no impact on the typical downstream user.

### Impact

Any action that can taken by a user can be carried out by an attacker via a malicious webpage. The scope of this vulnerability varies from sensitive data exfiltration (account credentials) to a complete takeover of the underlying system (deployment dependent).

The application connects to and authenticates with several outside websites and related services. Successful exploitation of this vulnerability may lead to the exposure of certain credentials saved by the application to the attacker (such as passkeys or API keys). This exposure may lead to possible compromise of user accounts on connected websites and services. Some accounts are once-per-lifetime and compromise or abuse may lead to permanent loss of access.

Additionally, due to the built-in External Programs manager, successful exploitation of this vulnerability may lead to a compromise of the underlying system, including possible callbacks to an attacker-controlled server or established c2. **Successful exploitation of this mechanism leads to a compromise of the host or container**, depending on if the installation is native or containerized, in the user-context of the application (often root/privileged).

This exposure can occur without alerting the user. Certain actions may be logged by the qui log service, but removal of these log entries may be possible following a compromise of the host or container.

### Conditions

AT:P is set due to the prerequisite that the application not be accessed via `localhost` or `127.0.0.1`, as many modern browsers now have additional layers of protection for external->internal cross-origin requests. Some browsers may be impacted, but the likelihood is reduced. Users that access via any other domain or IP address are impacted.

UI:P is set due to the requirement that a malicious webpage be loaded by the browser, whether that be by way of a typo-squatted domain, malicious application, social engineering, or otherwise. Some services may automatically load webpages upon receipt in order to render a preview (i.e. certain IRC clients or other web apps used for communications), leading to an edge case where exploitation may sometimes occur without any intentional interaction by the user.

Knowledge of the target hostname is required, which may be obtained through various forms of enumeration or social engineering.

### Mitigation in lieu of update

Users who use a unique hostname, do not provide that hostname to untrusted persons or services, run a containerized instance, do not click on or automatically load untrusted webpages, and do not expose their instance to the greater internet for simplified discovery and attribution, have already reduced their exposure significantly. These mitigating factors already apply to most users. Simply signing out after use can reduce this exposure even further.

**Due to the conditions under which successful exploitation can occur, we do not expect to see regular exploitation of this item in the wild outside of highly targeted attacks reliant on the use of social engineering.**

## References
- https://github.com/autobrr/qui/security/advisories/GHSA-h8vw-ph9r-xpch
- https://nvd.nist.gov/vuln/detail/CVE-2026-30924
- https://github.com/autobrr/qui/commit/424f7a0de089dce881e8bbecd220163a78e0295f
- https://github.com/autobrr/qui
