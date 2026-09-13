# [C] mppx has multiple payment bypass and griefing vulnerabilities

## Summary
Severity: Critical
Advisory: GHSA-8x4m-qw58-3pcx
CWE: CWE-288, CWE-294, CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-8x4m-qw58-3pcx
Type: github-advisory

## Affected
- npm: `mppx` — affected >=0 <0.4.8

## Details
### Impact

Multiple vulnerabilities were discovered in `tempo/charge` and `tempo/session` which allowed for undesirable behaviors, including:
- Replaying `tempo/charge` transaction hashes across push/pull modes, across charge/session endpoints, and via concurrent requests
- Performing free `tempo/charge` requests due to missing transfer log verification in pull-mode
- Replaying `tempo/charge` credentials across routes via cross-route scope confusion (`memo`/`splits` not included in scope binding)
- Manipulating the fee payer of a `tempo/charge` handler into paying for requests (missing sender signature before co-signing)
- Bypassing `tempo/session` voucher signature verification
- Piggybacking off existing `tempo/session` channels via settle voucher reuse and weak channel ID binding
- Performing free `tempo/session` requests by exploiting channel reopen without on-chain settled state
- Accepting deductions on finalized `tempo/session` channels
- Bypassing payment on free routes via method-mismatch fallback
- Griefing `tempo/session` channels via force-close detection bypass (`closeRequestedAt` not persisted)

### Patches

Fixed in 0.4.8.

### Workarounds

There are no workarounds available for these vulnerabilities.

## References
- https://github.com/wevm/mppx/security/advisories/GHSA-8x4m-qw58-3pcx
- https://github.com/wevm/mppx
