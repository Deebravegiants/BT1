# [C] CVE-2023-27482

## Summary
Severity: Critical
Advisory: CVE-2023-27482
Aliases: GHSA-2j8f-h4mr-qr25
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-03-08
Source: https://osv.dev/vulnerability/CVE-2023-27482
Type: osv

## Details
homeassistant is an open source home automation tool. A remotely exploitable vulnerability bypassing authentication for accessing the Supervisor API through Home Assistant has been discovered. This impacts all Home Assistant installation types that use the Supervisor 2023.01.1 or older. Installation types, like Home Assistant Container (for example Docker), or Home Assistant Core manually in a Python environment, are not affected. The issue has been mitigated and closed in Supervisor version 2023.03.1, which has been rolled out to all affected installations via the auto-update feature of the Supervisor. This rollout has been completed at the time of publication of this advisory. Home Assistant Core 2023.3.0 included mitigation for this vulnerability. Upgrading to at least that version is thus advised. In case one is not able to upgrade the Home Assistant Supervisor or the Home Assistant Core application at this time, it is advised to not expose your Home Assistant instance to the internet.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27482.json
- https://github.com/elttam/publications/blob/master/writeups/home-assistant/supervisor-authentication-bypass-advisory.md
- https://github.com/home-assistant/core/security/advisories/GHSA-2j8f-h4mr-qr25
- https://nvd.nist.gov/vuln/detail/CVE-2023-27482
- https://www.elttam.com/blog/pwnassistant/
- https://www.home-assistant.io/blog/2023/03/08/supervisor-security-disclosure/
