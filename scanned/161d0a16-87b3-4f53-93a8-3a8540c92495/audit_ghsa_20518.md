# [M] Username spoofing in OnionShare

## Summary
Severity: Medium
Advisory: GHSA-68vr-8f46-vc9f
CVE: CVE-2022-21696
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-68vr-8f46-vc9f
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.3 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/). This is an issue from that penetration test.

- Vulnerability ID: OTF-005
- Vulnerability type: Improper Input Sanitization
- Threat level: Low

## Description:

It is possible to change the username to that of another chat participant with an additional space character at the end of the name string.

## Technical description:

Assumed users in Chat:

- Alice
- Bob
- Mallory

1. Mallory renames to `Alice `.
2. Mallory sends message as `Alice `.
3. Alice and Bob receive a message from Mallory disguised as `Alice `, which is hard to distinguish from the `Alice`
in the web interface.

![otf-005-a](https://user-images.githubusercontent.com/156128/140666112-8febd4d8-6761-41aa-955c-48be76f3c657.png)
![otf-005-b](https://user-images.githubusercontent.com/156128/140666113-1713ddf7-cef6-4dac-b718-9af1dc4ffdcd.png)

Other (invisible) whitespace characters were found to be working as well.

## Impact:

An adversary with access to the chat environment can use the rename feature to impersonate other participants by adding whitespace characters at the end of the username.

## Recommendation:

- Remove non-visible characters from the username

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-68vr-8f46-vc9f
- https://nvd.nist.gov/vuln/detail/CVE-2022-21696
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-47.yaml
