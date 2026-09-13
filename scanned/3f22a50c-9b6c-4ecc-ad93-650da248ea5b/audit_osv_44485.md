# [H] Broken access control in AshPhoenix SubdomainHook via a nil tenant in handle_subdomain

## Summary
Severity: High
Advisory: CVE-2026-82724
Aliases: EEF-CVE-2026-82724, GHSA-39c8-xcwr-gqff
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82724
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash_phoenix invokes the SubdomainHook authorization callback with a nil tenant, so tenant-scoped access checks never see the tenant they are meant to enforce.

AshPhoenix.LiveView.SubdomainHook.on_mount/4 attached a handle_params hook to assign the tenant and then immediately called handle_subdomain in the same on_mount. The tenant assign is only written when LiveView later runs handle_params, strictly after on_mount returns, so handle_subdomain read an unset assign and ran as apply(m, f, [socket, nil | a]). A consumer gate that halts when the user does not belong to the tenant instead evaluated nil, either crashing or taking a permissive branch, and it was never re-run once the real subdomain was assigned or on later navigations. The fix runs handle_subdomain inside the handle_params hook with the real tenant on every navigation.

This issue affects ash_phoenix: from 2.1.26 before 2.3.25.

## References
- https://cna.erlef.org/cves/CVE-2026-82724.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82724
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82724.json
- https://github.com/ash-project/ash_phoenix/security/advisories/GHSA-39c8-xcwr-gqff
- https://nvd.nist.gov/vuln/detail/CVE-2026-82724
- https://github.com/ash-project/ash_phoenix/commit/b396e1aa5c6bdec39255f19cf938b539e6d28b71
- https://github.com/ash-project/ash_phoenix
