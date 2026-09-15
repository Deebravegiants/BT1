# [H] CoreDNS' transfer stanza selection uses lexicographic compare (subzone ACL bypass)

## Summary
Severity: High
Advisory: GHSA-h8mm-c463-wjq3
CVE: CVE-2026-33489
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-h8mm-c463-wjq3
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.3

## Details
### Summary
CoreDNS' transfer plugin can select the wrong ACL stanza when both a parent zone and a more-specific subzone are configured. A permissive parent-zone transfer rule can override a restrictive subzone rule (name-dependent), allowing an unauthorized client to perform AXFR/IXFR for the subzone and retrieve its zone contents.

### Details
In plugin/transfer/transfer.go, stanza selection is implemented by longestMatch(), which is documented as "longest zone match wins", but it actually chooses the winner via a lexicographic string comparison:
- zone := "" // longest zone match wins (plugin/transfer/transfer.go)
- if z > zone { zone = z; x = xfr } (plugin/transfer/transfer.go)

So, a parent zone like example.org. can beat a child zone like a.example.org. purely due to lexicographic ordering ("example.org." > "a.example.org."), even though the child zone is the longer/more specific suffix match. The bypass is data-dependent (some child labels will win, some will lose), making it operationally non-intuitive.

### PoC
1. Adjust COREDNS_BIN in the PoC to point at right path (see the top-level const definitions for tunables as well)
2. Run python3 ./acl-repro.py
3. Expected output:
*** Baseline (only subzone transfer rule) ***
axfr a.example.org.: rcode=5 ancount=0 (expected REFUSED=5)

*** Candidate (add permissive parent transfer rule) ***
axfr a.example.org.: rcode=0 ancount=5 (expected NOERROR=0 with ancount>0)

*** OK ***
Subzone transfer ACL bypass reproduced: adding a permissive parent-zone stanza can override a stricter child-zone stanza due to lexicographic zone selection.

### Impact
Unauthorized zone transfer can expose full zone contents to a remote network client that was intended to be denied by a subzone-specific transfer policy.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-h8mm-c463-wjq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33489
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.3
