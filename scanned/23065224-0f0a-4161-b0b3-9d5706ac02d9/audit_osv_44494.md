# [M] Ash.Policy.Authorizer returns records denied by a runtime read policy to any actor

## Summary
Severity: Medium
Advisory: CVE-2026-82747
Aliases: EEF-CVE-2026-82747, GHSA-4259-gvr2-4xhq
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82747
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash returns records that a runtime read policy denies to any actor.

When a resource has an access_type :runtime read policy (a check evaluated per record rather than compiled to a filter), Ash.Policy.Authorizer decides each record in check_result/1 (lib/ash/policy/authorizer/authorizer.ex) by discarding impossible policy scenarios and inspecting what remains. When every scenario for a record was impossible, meaning no policy can authorize it and it must be forbidden, the empty-scenario branch instead kept the record ({[record | data], authorizer, any_forbidden?}) and returned it as authorized. As a result, records the runtime read policy denies are returned to any actor. The fix forbids a record whose scenarios are all impossible.

This issue affects ash: from 3.4.44 before 3.32.2.

## References
- https://cna.erlef.org/cves/CVE-2026-82747.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82747
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82747.json
- https://github.com/ash-project/ash/security/advisories/GHSA-4259-gvr2-4xhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-82747
- https://github.com/ash-project/ash/commit/6eddb8ab26e45023faf0c79ebd152bb40aefda02
- https://github.com/ash-project/ash
