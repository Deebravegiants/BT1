# [H] Out-of-bounds Read in Onionshare

## Summary
Severity: High
Advisory: GHSA-x7wr-283h-5h2v
CVE: CVE-2022-21688
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-x7wr-283h-5h2v
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=0 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/). This is an issue from that penetration test.

- Vulnerability ID: OTF-014
- Vulnerability type: Out-of-bounds Read
- Threat level: Elevated

## Description:

The desktop application was found to be vulnerable to denial of service via an undisclosed vulnerability in the QT image parsing.

## Technical description:

Prerequisites:

- Onion address is known
- Public service or authentication is valid
- Desktop application is used
- History is displayed

The rendering of images found in OTF-001 (page 25) could be elevated to a Denial of Service, which requires only very few bytes to be sent as a path parameter to any of the Onionshare functions. Roughly 20 bytes lead to 2GB memory consumption and this can be triggered multiple times. To be abused, this vulnerability requires rendering in the history tab, so some user interaction is required. The issue is in the process of disclosure to the QT security mailing list. More details will be provided after a fixed QT build has been deployed.

## Impact:

An adversary with knowledge of the Onion service address in public mode or with authentication in private mode can perform a Denial of Service attack, which quickly results in out-of-memory for the server. This requires the desktop application with rendered history, therefore the impact is only elevated.

## Recommendation:

- Monitor for upstream fix
- Fix OTF-001 (page 25) as a workaround

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-x7wr-283h-5h2v
- https://nvd.nist.gov/vuln/detail/CVE-2022-21688
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-39.yaml
