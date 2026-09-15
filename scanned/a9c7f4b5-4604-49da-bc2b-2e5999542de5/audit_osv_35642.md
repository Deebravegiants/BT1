# [C] pgAdmin 4: Unauthenticated pickle deserialization in SQL Editor close / update_connection routes enables remote code execution

## Summary
Severity: Critical
Advisory: CVE-2026-12046
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-12046
Type: osv

## Details
Two state-mutating endpoints in pgAdmin 4's SQL Editor blueprint -- DELETE /sqleditor/close/<trans_id> and POST /sqleditor/initialize/sqleditor/update_connection/<sgid>/<sid>/<did> -- were the only routes in the module missing the @pga_login_required decorator. Both reach a pickle.loads sink on session['gridData'][<trans_id>]['command_obj']: the close endpoint via close_sqleditor_session(), and update_sqleditor_connection via check_transaction_status(). In server mode these endpoints were reachable without any authenticated pgAdmin session.

The defect is a missing-authentication-on-critical-function (CWE-306) wrapper around a deserialization-of-untrusted-data sink (CWE-502). Exploiting it for remote code execution requires the attacker to also forge a server-side session file whose gridData entry contains a malicious pickle payload, which in turn requires both (a) knowledge of pgAdmin's Flask SECRET_KEY (no chain to leak it is described here -- the attacker must already possess it) and (b) write access to pgAdmin's sessions/ directory on the host. Neither precondition is granted by this defect on its own. When those preconditions are met from another channel (misconfigured deployment, prior compromise, leaked configuration), the missing auth gate is the final hop that turns an existing partial compromise into unauthenticated code execution in the pgAdmin process -- and, by extension, on the host under whatever account runs pgAdmin.

Fix is a one-line @pga_login_required decorator on each of the two endpoints, matching the convention used by every other route in the module. The is_authenticated / MFA chain now runs before the trans_id is dereferenced, so an unauthenticated request is rejected before reaching the deserialization path.

The defect is server-mode only. In DESKTOP mode pgAdmin's before_request hook re-authenticates DESKTOP_USER on every request, so no endpoint can be exercised in an unauthenticated state and no auth decorator (or its absence) is meaningful. The accompanying regression test mirrors the attacker's path -- harvests an X-pgA-CSRFToken from GET /login and replays it against both endpoints -- and self-skips outside server mode for that reason; it is wired into the existing server-mode CI workflow alongside the data-isolation tests.

This issue affects pgAdmin 4: from 6.9 before 9.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12046
- https://github.com/pgadmin-org/pgadmin4/issues/10072
- https://github.com/pgadmin-org/pgadmin4/commit/f81433ae2f998f95bb17f27f53b4e99ebcc1df9c
- https://github.com/pgadmin-org/pgadmin4
