# [M] Stream description leaks to ex-subscribers in Zulip

## Summary
Severity: Medium
Advisory: CVE-2023-47642
Aliases: GHSA-c9wc-65fh-9x8p
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-16
Source: https://osv.dev/vulnerability/CVE-2023-47642
Type: osv

## Details
Zulip is an open-source team collaboration tool. It was discovered by the Zulip development team that active users who had previously been subscribed to a stream incorrectly continued being able to use the Zulip API to access metadata for that stream. As a result, users who had been removed from a stream, but still had an account in the organization, could still view metadata for that stream (including the stream name, description, settings, and an email address used to send emails into the stream via the incoming email integration). This potentially allowed users to see changes to a stream’s metadata after they had lost access to the stream. This vulnerability has been addressed in version 7.5 and all users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47642.json
- https://github.com/zulip/zulip/security/advisories/GHSA-c9wc-65fh-9x8p
- https://nvd.nist.gov/vuln/detail/CVE-2023-47642
- https://github.com/zulip/zulip/commit/6336322d2f9bbccaacfc80cba83a3c62eefd5737
