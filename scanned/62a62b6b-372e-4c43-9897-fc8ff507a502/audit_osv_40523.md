# [M] Atom-table exhaustion denial-of-service via JSON parse_document in MDEx

## Summary
Severity: Medium
Advisory: CVE-2026-53426
Aliases: EEF-CVE-2026-53426, GHSA-923r-7vf4-5vw8
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-53426
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in leandrocp MDEx allows Excessive Allocation.

MDEx.parse_document/2 accepts a {:json, json} source. In lib/mdex.ex, the private json_to_node/1 function passes the attacker-controlled node_type value to Module.concat/1, which calls String.to_atom/1 and interns a brand-new atom for every distinct value. Atoms are never garbage collected on the BEAM, so a crafted JSON document carrying a unique node_type at each (deeply nested) node mints one permanent atom per node.

A single document can intern hundreds of thousands of atoms, and a large enough document exhausts the default atom table (around 1,048,576 atoms) and aborts the entire Erlang VM, taking down every process on the node. Any application that passes untrusted input to the {:json, ...} source of MDEx.parse_document is exposed to an unauthenticated denial-of-service.

This issue affects mdex from 0.4.3 before 0.13.2.

## References
- https://cna.erlef.org/cves/CVE-2026-53426.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-53426
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53426.json
- https://github.com/leandrocp/mdex/security/advisories/GHSA-923r-7vf4-5vw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53426
- https://github.com/leandrocp/mdex/commit/00fddf444220a1f1cc0af0a1cab6738804878387
- https://github.com/leandrocp/mdex
