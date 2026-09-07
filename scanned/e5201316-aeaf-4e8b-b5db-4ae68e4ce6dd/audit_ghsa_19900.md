# [H] Aim Vulnerable to Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-fx47-jpv9-7hxr
CVE: CVE-2024-10110
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-fx47-jpv9-7hxr
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=3.15.0

## Details
In version 3.23.0 of aimhubio/aim, the ScheduledStatusReporter object can be instantiated to run on the main thread of the tracking server, leading to the main thread being blocked indefinitely. This results in a denial of service as the tracking server becomes unable to respond to other requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10110
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/a566d4a2501c96a545a3c89d92af6ad7e7e0da99/aim/sdk/reporter/__init__.py#L789
- https://huntr.com/bounties/5ea6cf56-7b4c-4dce-9b6c-3e910fbb1ae4
