# [M] UpTrain has a Constant Default API Key

## Summary
Severity: Medium
Advisory: CVE-2025-27621
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2025-27621
Type: osv

## Details
UpTrain is an open-source platform to evaluate and improve generative AI applications. In version 0.7.1 and prior, the UpTrain backend creates a new default user with a static username, where the username is also used as the default API key. The UpTrain backend also has an open CORS policy. Using these two primitives, any website can make a authenticated cross-origin request to the UpTrain instance by providing the default API key in the header `uptrain-access-token`. This issue may allow arbitrary websites to perform privileged operations on the UpTrain instance, as if they were the default logged in user. As of time of publication, no known patches are available.

## References
- https://github.com/uptrain-ai/uptrain/blob/a31cc14eddcb6c0b0b12cbed15f086d98c441c6f/uptrain/dashboard/backend/app.py#L105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27621.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27621
- https://securitylab.github.com/advisories/GHSL-2024-198_GHSL-2024-199_Uptrain/
