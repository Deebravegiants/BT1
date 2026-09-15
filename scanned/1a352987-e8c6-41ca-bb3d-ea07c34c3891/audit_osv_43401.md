# [C] FreePBX: Unauthenticated SQL injection in FreePBX missedcall via inbound Caller ID name leads to administrator takeover

## Summary
Severity: Critical
Advisory: CVE-2026-73663
Aliases: GHSA-g27h-xf3q-h3rm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73663
Type: osv

## Details
FreePBX is an open source IP PBX. From 16.0.0 until 16.0.11 and 17.0.4, the FreePBX missedcall module places the inbound Caller ID name from crafted SIP From headers into the missedcalllog INSERT in agi-bin/missedcallnotify.php without escaping or bound parameters. An unauthenticated caller can inject SQL when a monitored extension goes unanswered, corrupting the database and modifying FreePBX administrator accounts to obtain unauthorized remote access. This issue is fixed in versions 16.0.11 and 17.0.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73663.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-g27h-xf3q-h3rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-73663
- https://github.com/FreePBX/missedcall/commit/4ada1d6b280fc246e74babc8d52f4cd1509eff24
- https://github.com/FreePBX/missedcall/commit/710acdf51968db507b3f9c47ce3db006846cf44c
