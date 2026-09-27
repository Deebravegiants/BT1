# [M] CVE-2018-1999017

## Summary
Severity: Medium
Advisory: CVE-2018-1999017
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999017
Type: osv

## Details
Pydio version 8.2.0 and earlier contains a Server-Side Request Forgery (SSRF) vulnerability in plugins/action.updater/UpgradeManager.php Line: 154, getUpgradePath($url) that can result in an authenticated admin users requesting arbitrary URL's, pivoting requests through the server. This attack appears to be exploitable via the attacker gaining access to an administrative account, enters a URL into Upgrade Engine, and reloads the page or presses "Check Now". This vulnerability appears to have been fixed in 8.2.1.

## References
- https://pydio.com/en/community/releases/pydio-core/pydio-821-security-release
- https://www.mike-gualtieri.com/files/Pydio-8-VulnerabilityDisclosure-Jul18.txt
