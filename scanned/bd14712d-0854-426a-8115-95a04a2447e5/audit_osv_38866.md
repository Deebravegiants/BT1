# [C] Apache Polaris: staged table creation could vend storage credentials for unvalidated locations

## Summary
Severity: Critical
Advisory: CVE-2026-42809
Aliases: GHSA-8ggj-j522-h5qf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42809
Type: osv

## Details
Apache Polaris can issue broad temporary ("vended") storage credentials during
staged
table creation before the effective table location has been validated or
durably reserved. 
Those temporary credentials are meant to limit the scope
of
accessible table data and metadata, but this scope limitation becomes
attacker-
directed because the attacker can choose a reachable target location.



In the confirmed variant, if the caller supplies a custom `location` during
stage create and requests credential vending, Apache Polaris uses that location to
construct delegated storage credentials immediately. The stage-create path
itself neither runs the normal location validation nor the overlap checks
before those credentials are issued.



Closely related to that, the staged-create flow also accepts
`write.data.path` / `write.metadata.path` in the request properties and
feeds
those location overrides into the same effective table location set used for
credential vending. Those fields are secondary to the main custom-`location`
exploit, but they are still attacker-influenced location inputs that should
be
validated before any credentials are issued.

## References
- http://www.openwall.com/lists/oss-security/2026/05/02/10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42809.json
- https://lists.apache.org/thread/8tfsr8y7pgq6rdcvjx95hkcr47td671r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42809
