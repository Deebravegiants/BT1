# [M] OpenNMS JEXL sandbox bypass in Measurements REST API allows ROLE_USER to load arbitrary classes

## Summary
Severity: Medium
Advisory: CVE-2026-19135
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-19135
Type: osv

## Details
A JEXL expression sandbox bypass exists in multiple versions of OpenNMS Meridian and Horizon. A low-privileged authenticated user can submit a crafted expression to the Measurements REST API that escapes the sandbox and loads arbitrary Java classes on the server. This can potentially allow an attacker to gain access to confidential information and compromise integrity.

The solution is to upgrade to Meridian 2024.3.12, 2025.0.9 and Horizon 36.0.3 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet.

## References
- https://github.com/OpenNMS
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19135
- https://github.com/OpenNMS/opennms/pull/8754
