# [M] Unbounded handle_error recursion enables denial of service in AshOban triggers

## Summary
Severity: Medium
Advisory: CVE-2026-78228
Aliases: EEF-CVE-2026-78228, GHSA-94p7-498r-mrhp
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-78228
Type: osv

## Details
Uncontrolled Recursion vulnerability in ash-project ash_oban allows a user who can drive a trigger's on_error action to fail on the final attempt to exhaust worker CPU and memory, denying service.

The generated worker's atomic handle_error/4 runs the trigger's on_error action on a job's final attempt inside a rescue that, when the action itself raises, calls handle_error/4 again with the same job. The job's attempt still equals max_attempts, so it re-enters the same clause and re-runs the failing action, with no exit. Any deterministic on_error failure (a data-layer outage, a misconfigured action, or a record the action rejects) loops forever; because the recursive call is not in tail position, each iteration retains a formatted stacktrace and the process heap grows without bound while the failing statement is re-issued against the data layer until the runtime kills the worker.

This issue affects ash_oban: from 0.8.0-rc.1 before 0.8.14.

## References
- https://cna.erlef.org/cves/CVE-2026-78228.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-78228
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78228.json
- https://github.com/ash-project/ash_oban/security/advisories/GHSA-94p7-498r-mrhp
- https://nvd.nist.gov/vuln/detail/CVE-2026-78228
- https://github.com/ash-project/ash_oban/commit/851cd0e76ed882bf736fc48d10f96d037e26b5f0
- https://github.com/ash-project/ash_oban
