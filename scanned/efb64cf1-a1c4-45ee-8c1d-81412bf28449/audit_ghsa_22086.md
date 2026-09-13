# [M] Ejabberd DoS via malformed stanza

## Summary
Severity: Medium
Advisory: GHSA-2h3q-v47h-f4rc
CVE: CVE-2011-4320
CWE: CWE-400
Ecosystem: Hex
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2h3q-v47h-f4rc
Type: github-advisory

## Affected
- Hex: `ejabberd` — affected >=0 <2.1.9
- Hex: `ejabberd` — affected >=3.0.0-alpha-1 <3.0.0-alpha-4

## Details
The `mod_pubsub` module (mod_pubsub.erl) in ejabberd 2.1.8 and 3.0.0-alpha-3 allows remote authenticated users to cause a denial of service (infinite loop) via a stanza with a publish tag that lacks a node attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4320
- https://github.com/processone/ejabberd/commit/d3c4eab46f3cd54f7686cfed740d9c130b6801cf
- https://github.com/processone/ejabberd/commit/d5b4d6785879f0a5192c26f5b5e218aec8104798
- https://github.com/processone/ejabberd
- https://support.process-one.net/browse/EJAB-1498
- http://www.openwall.com/lists/oss-security/2011/11/19/1
- http://www.openwall.com/lists/oss-security/2011/11/19/2
- http://www.process-one.net/en/ejabberd/release_notes/release_note_ejabberd_2.1.9
