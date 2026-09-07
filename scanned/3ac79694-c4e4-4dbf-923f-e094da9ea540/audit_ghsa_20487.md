# [M] Path traversal in Onionshare

## Summary
Severity: Medium
Advisory: GHSA-jgm9-xpfj-4fq6
CVE: CVE-2022-21693
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-jgm9-xpfj-4fq6
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=2.3 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/). This is an issue from that penetration test.

- Vulnerability ID: OTF-013
- Vulnerability type: Improper Hardening
- Threat level: Low

## Description:

The filesystem restriction could be hardened and should only allow for pre-defined subfolders.

## Technical description:

The Flatpak and Snap configurations allow for read-only access on the whole home folder. The relevant lines in the configuration files are `onionshare/snap/snapcraft.yaml#L20` and `onionshare/flatpak/org.onionshare.OnionShare.yaml#L19` , respectively.

The encapsulation of filesystem access via these mechanisms should be restricted to pre-defined folders and not allow for access to (configuration) files outside the Onionshare-specific folders.

Sadly Snap does not allow for further restriction to specific folders and therefore cannot be further hardened. By default both frameworks disallow access to hidden folders and therefore reduce the potential impact.

## Impact:

An adversary with a primitive that allows for filesystem access from the context of the Onionshare process can access sensitive files in the entire user home folder. This could lead to the leaking of sensitive data. Due to the automatic exclusion of hidden folders, the impact is reduced.

## Recommendation:

- Reduce read access in Flatpak configuration.

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-jgm9-xpfj-4fq6
- https://nvd.nist.gov/vuln/detail/CVE-2022-21693
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-44.yaml
