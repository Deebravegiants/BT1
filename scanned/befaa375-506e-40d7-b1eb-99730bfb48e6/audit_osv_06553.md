# [H] BIT-mastodon-2022-46405

## Summary
Severity: High
Advisory: BIT-mastodon-2022-46405
Aliases: CVE-2022-46405
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2022-46405
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=0 <4.0.3

## Details
Mastodon through 4.0.2 allows attackers to cause a denial of service (large Sidekiq pull queue) by creating bot accounts that follow attacker-controlled accounts on certain other servers associated with a wildcard DNS A record, such that there is uncontrolled recursion of attacker-generated messages.

## References
- https://borg.social/notes/98bcoo2t1n
- https://hackmd.io/rD9nsTz1QeuPT-erxqjY-A
- https://nvd.nist.gov/vuln/detail/CVE-2022-46405
