# [H] Authentication Bypass in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-1646
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-1646
Type: osv

## Details
parisneo/lollms-webui is vulnerable to authentication bypass due to insufficient protection over sensitive endpoints. The application checks if the host parameter is not '0.0.0.0' to restrict access, which is inadequate when the application is bound to a specific interface, allowing unauthorized access to endpoints such as '/restart_program', '/update_software', '/check_update', '/start_recording', and '/stop_recording'. This vulnerability can lead to denial of service, unauthorized disabling or overriding of recordings, and potentially other impacts if certain features are enabled in the configuration.

## References
- https://huntr.com/bounties/2f769c46-aa85-4ab8-8b08-fe791313b7ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1646.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1646
- https://github.com/parisneo/lollms-webui/commit/02e829b5653a1aa5dbbe9413ec84f96caa1274e8
