# [H] raspap-webgui in RaspAP 2.6.6 allows attackers to execute commands as root because of the insecure sudoers permissions.

## Summary
Severity: High
Advisory: GHSA-536p-4pcj-5mr9
CVE: CVE-2021-38557
CWE: CWE-276, CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-536p-4pcj-5mr9
Type: github-advisory

## Affected
- Packagist: `billz/raspap-webgui` — affected >=0

## Details
raspap-webgui in RaspAP 2.6.6 allows attackers to execute commands as root because of the insecure sudoers permissions. The www-data account can execute /etc/raspap/hostapd/enablelog.sh as root with no password; however, the www-data account can also overwrite /etc/raspap/hostapd/enablelog.sh with any executable content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38557
- https://github.com/RaspAP/raspap-webgui
- https://github.com/RaspAP/raspap-webgui/blob/fabc48c7daae4013b9888f266332e510b196a062/installers/raspap.sudoers
- https://zerosecuritypenetrationtesting.com/?page_id=306
