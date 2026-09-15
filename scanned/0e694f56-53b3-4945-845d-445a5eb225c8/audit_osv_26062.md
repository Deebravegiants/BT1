# [M] Blind SSRF in /home/testslack endpoint

## Summary
Severity: Medium
Advisory: CVE-2023-50259
Aliases: GHSA-8mcr-vffr-jwxv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-22
Source: https://osv.dev/vulnerability/CVE-2023-50259
Type: osv

## Details
Medusa is an automatic video library manager for TV shows. Versions prior to 1.0.19 are vulnerable to unauthenticated blind server-side request forgery (SSRF). The `testslack` request handler in `medusa/server/web/home/handler.py` does not validate the user-controlled `slack_webhook` variable and passes it to the `notifiers.slack_notifier.test_notify` method, then `_notify_slack` and finally `_send_slack` method,  which sends a POST request to the user-controlled URL on line 103 in `/medusa/notifiers/slack.py`, which leads to a blind server-side request forgery (SSRF). This issue allows for crafting POST requests on behalf of the Medusa server. Version 1.0.19 contains a fix for the issue.

## References
- https://github.com/pymedusa/Medusa/blob/3d656652ab277e47689483912ed7fc443e7023e8/medusa/notifiers/slack.py#L103
- https://github.com/pymedusa/Medusa/blob/3d656652ab277e47689483912ed7fc443e7023e8/medusa/server/web/home/handler.py#L168
- https://github.com/pymedusa/Medusa/releases/tag/v1.0.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50259.json
- https://github.com/pymedusa/Medusa/security/advisories/GHSA-8mcr-vffr-jwxv
- https://nvd.nist.gov/vuln/detail/CVE-2023-50259
- https://securitylab.github.com/advisories/GHSL-2023-201_GHSL-2023-202_Medusa/
