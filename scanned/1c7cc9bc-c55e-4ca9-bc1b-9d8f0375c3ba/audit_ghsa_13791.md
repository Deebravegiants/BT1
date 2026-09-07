# [M] Ethyca Fides HTML Injection Vulnerability in HTML-Formatted DSR Packages

## Summary
Severity: Medium
Advisory: GHSA-3vpf-mcj7-5h38
CVE: CVE-2023-47114
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-11-08
Source: https://github.com/advisories/GHSA-3vpf-mcj7-5h38
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=2.15.1 <2.23.3

## Details
### Impact

The Fides web application allows data subject users to request access to their personal data. If the request is approved by the data controller user operating the Fides web application, the data subject's personal data can then retrieved from connected systems and data stores before being bundled together as a data subject access request package for the data subject to download. Supported data formats for the package include json and csv, but the most commonly used format is a series of HTML files compressed in a ZIP file. Once downloaded and unzipped, the data subject user can browse the HTML files on their local machine.

It was identified that there was no validation of input coming from e.g. the connected systems and data stores which is later reflected in the downloaded data. This can result in an HTML injection that can be abused e.g. for phishing attacks or malicious JavaScript code execution, but only in the context of the data subject's browser accessing a HTML page using the `file://` protocol.

Exploitation is limited to rogue Admin UI users, malicious connected system / data store users, and the data subject user if tricked via social engineering into submitting malicious data themselves.

### Patches
The vulnerability has been patched in Fides version `TBC`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds
Only Fides deployments which have been configured to use `html` as the package format in the [storage destination](https://docs.ethyca.com/dev-docs/configuration/privacy-requests/storage-destinations) are vulnerable. Using `json` or `csv` instead eliminates this vulnerability.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-3vpf-mcj7-5h38
- https://nvd.nist.gov/vuln/detail/CVE-2023-47114
- https://github.com/ethyca/fides/commit/50360a0e24aac858459806bb140bb1c4b71e67a1
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.23.3
