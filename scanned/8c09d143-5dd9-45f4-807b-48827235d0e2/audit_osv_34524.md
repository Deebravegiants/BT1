# [H] BigBlueButton vulnerable to DoS via PollSubmitVote GraphQL mutation

## Summary
Severity: High
Advisory: CVE-2025-61601
Aliases: GHSA-73j3-v3fq-fqx5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-61601
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. A Denial of Service (DoS) vulnerability in versions prior to 3.0.13 allows any authenticated user to freeze or crash the entire server by abusing the polling feature's `Choices` response type. By submitting a malicious payload with a massive array in the `answerIds` field, the attacker can cause the current meeting — and potentially all meetings on the server — to become unresponsive. Version 3.0.13 contains a patch. No known workarounds are available.

## References
- https://www.youtube.com/watch?v=BwROSVIYjOY
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61601.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-73j3-v3fq-fqx5
- https://nvd.nist.gov/vuln/detail/CVE-2025-61601
- https://github.com/bigbluebutton/bigbluebutton/pull/23662
