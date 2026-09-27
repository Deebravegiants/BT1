# [M] FORT-validator Vulnerable to RRDP Shared Snapshot Cache Poisoning

## Summary
Severity: Medium
Advisory: CVE-2026-53499
Aliases: GHSA-qfm3-577x-rh54
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53499
Type: osv

## Details
FORT Validator is a Resource Public Key Infrastructure (RPKI) relying-party validator that produces validated route-origin data. FORT Validator versions through 1.6.7 contain an origin-validation error in their RRDP processing: a delegated CA under the same Trust Anchor Locator (TAL) can reference a victim CA’s public RRDP notification and snapshot URLs, causing FORT’s URL-based download cache to report success after deleting the victim’s local snapshot. Following a routine victim publication, this can silently remove the victim’s VRPs and other signed objects from FORT’s output, potentially enabling route hijacking or loss of reachability. Version 1.6.8 contains a patch that rejects cross-origin RRDP snapshot and delta URLs; as a workaround, administrators can disable HTTP/RRDP with  --http.enabled=false  while keeping rsync enabled, although this can leave data unavailable or stale where rsync is not supported.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53499.json
- https://github.com/NICMx/FORT-validator/security/advisories/GHSA-qfm3-577x-rh54
- https://nvd.nist.gov/vuln/detail/CVE-2026-53499
