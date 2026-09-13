# [H] CVE-2019-7611

## Summary
Severity: High
Advisory: CVE-2019-7611
Aliases: GHSA-fj32-6v7m-57pg
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-7611
Type: osv

## Details
A permission issue was found in Elasticsearch versions before 5.6.15 and 6.6.1 when Field Level Security and Document Level Security are disabled and the _aliases, _shrink, or _split endpoints are used . If the elasticsearch.yml file has xpack.security.dls_fls.enabled set to false, certain permission checks are skipped when users perform one of the actions mentioned above, to make existing data available under a new index/alias name. This could result in an attacker gaining additional permissions against a restricted index.

## References
- https://discuss.elastic.co/t/elastic-stack-6-6-1-and-5-6-15-security-update/169077
- https://www.elastic.co/community/security
