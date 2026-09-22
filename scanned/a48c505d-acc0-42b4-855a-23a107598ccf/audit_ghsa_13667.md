# [M] Clear Text Credentials Exposed via Onboarding Task

## Summary
Severity: Medium
Advisory: GHSA-qf3c-rw9f-jh7v
CVE: CVE-2023-48700
CWE: CWE-200, CWE-256
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-qf3c-rw9f-jh7v
Type: github-advisory

## Affected
- PyPI: `nautobot-device-onboarding` — affected >=2.0.0 <3.0.0

## Details
### Impact
When credentials are provided while creating an OnboardingTask they may be visible via the Job Results view under the Additional Data tab as args for the Celery Task execution. This only applies to OnboardingTasks that are created with credentials specified while on v2.0.0-2.0.2 of Nautobot Device Onboarding. This advisory does not apply earlier version or when using NAPALM_USERNAME & NAPALM_PASSWORD from nautobot_config.py

### Patches
v3.0.0

### Workarounds
None

### Recommendations
* Delete all Job Results for any onboarding task to remove clear text credentials from database entries that were run while on v2.0.X
* Upgrade to v3.0.0
* Rotate any exposed credential

## References
- https://github.com/nautobot/nautobot-plugin-device-onboarding/security/advisories/GHSA-qf3c-rw9f-jh7v
- https://nvd.nist.gov/vuln/detail/CVE-2023-48700
- https://github.com/nautobot/nautobot-plugin-device-onboarding
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot-device-onboarding/PYSEC-2023-288.yaml
