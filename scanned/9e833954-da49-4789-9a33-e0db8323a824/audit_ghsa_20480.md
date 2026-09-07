# [M] Incorrect Permission Assignment for Critical Resource in OnionShare

## Summary
Severity: Medium
Advisory: GHSA-h29c-wcm8-883h
CVE: CVE-2022-21694
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-h29c-wcm8-883h
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.2 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/). This is an issue from that penetration test.

- Vulnerability ID: OTF-006
- Vulnerability type: Broken Website Hardening Control
- Threat level: Low

## Description:

The CSP can be turned on or off but not configured for the specific needs of the website.

## Technical description:

The website mode of the application allows to use a hardened CSP, which will block any scripts and external resources. It is not possible to configure this CSP for individual pages and therefore the security enhancement cannot be used for websites using javascript or external resources like fonts or images.

If CSP were configurable, the website creator could harden it accordingly to the needs of the application.

As this issue correlates with the Github issue for exposing the flask application directly (https://github.com/onionshare/ onionshare/issues/1389), it can be assumed that this can be solved by either changing to a well-known webserver, which supports this kind of configuration, or enhancing the status quo by making the CSP a configurable part of each website.

We believe that bundling the nginx or apache webserver would add complexity and dependencies to the application that could result in a larger attack surface - as these packages receive regular security updates. On the other hand it is not recommended to directly expose the flask webserver, due to lack of hardening. This is a trade-off which needs to be evaluated by the Onionshare developers, as multiple features are involved. Ideally the application user could choose between the built-in flask webserver or a system webserver of choice.

## Impact:

As this is a general weakness and not a direct vulnerability in the Onionshare application, the direct impact of this issue is rather low.

## Recommendation:

- Consider offering a configurable webserver choice
- Consider configurable CSP

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-h29c-wcm8-883h
- https://nvd.nist.gov/vuln/detail/CVE-2022-21694
- https://github.com/onionshare/onionshare/issues/1389
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-45.yaml
