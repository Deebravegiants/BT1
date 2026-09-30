# [C] Pterodactyl Panel before 1.14.1 Privilege Escalation via Schedule Tasks

## Summary
Severity: Critical
Advisory: CVE-2026-86177
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86177
Type: osv

## Details
Pterodactyl Panel before 1.14.1 fails to validate action-specific permissions in scheduled task creation, allowing subusers with only schedule.update permission to execute arbitrary console commands. Attackers can create and immediately trigger scheduled tasks that run game-server console commands, control server power state, or create backups without proper authorization checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86177.json
- https://github.com/pterodactyl/panel/releases/tag/v1.14.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-86177
- https://www.vulncheck.com/advisories/pterodactyl-panel-before-1.14.1-privilege-escalation-via-schedule-tasks
- https://github.com/pterodactyl/panel/commit/913b354aff43ff04fce95357ed68a675a1dd0fa6
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/blob/v1.14.0/app/Http/Requests/Api/Client/Servers/Schedules/StoreTaskRequest.php#L10-L25
- https://github.com/pterodactyl/panel/blob/v1.14.0/app/Jobs/Schedule/RunTaskJob.php#L60-L75
- https://github.com/geo-chen/oss/blob/main/panel.md
