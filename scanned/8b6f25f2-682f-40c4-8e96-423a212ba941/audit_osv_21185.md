# [M] CVE-2021-41115

## Summary
Severity: Medium
Advisory: CVE-2021-41115
Aliases: GHSA-4h36-mqfq-42jg
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-07
Source: https://osv.dev/vulnerability/CVE-2021-41115
Type: osv

## Details
Zulip is an open source team chat server. In affected versions Zulip allows organization administrators on a server to configure "linkifiers" that automatically create links from messages that users send, detected via arbitrary regular expressions. Malicious organization administrators could subject the server to a denial-of-service via regular expression complexity attacks; most simply, by configuring a quadratic-time regular expression in a linkifier, and sending messages that exploited it. A regular expression attempted to parse the user-provided regexes to verify that they were safe from ReDoS -- this was both insufficient, as well as _itself_ subject to ReDoS if the organization administrator entered a sufficiently complex invalid regex. Affected users should [upgrade to the just-released Zulip 4.7](https://zulip.readthedocs.io/en/latest/production/upgrade-or-modify.html#upgrading-to-a-release), or [`main`](https://zulip.readthedocs.io/en/latest/production/upgrade-or-modify.html#upgrading-from-a-git-repository).

## References
- https://github.com/zulip/zulip/commit/e2d303c1bb5f538d17dc3d9134bc8858bdece781
- https://github.com/zulip/zulip/security/advisories/GHSA-4h36-mqfq-42jg
- https://securitylab.github.com/advisories/GHSL-2021-118-zulip-zulip/
