# [H] BIT-solr-2020-13941

## Summary
Severity: High
Advisory: BIT-solr-2020-13941
Aliases: CVE-2020-13941, GHSA-2467-h365-j7hm
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-solr-2020-13941
Type: osv

## Affected
- Bitnami: `solr` — affected >=0 <8.6.0

## Details
Reported in SOLR-14515 (private) and fixed in SOLR-14561 (public), released in Solr version 8.6.0. The Replication handler (https://lucene.apache.org/solr/guide/8_6/index-replication.html#http-api-commands-for-the-replicationhandler) allows commands backup, restore and deleteBackup. Each of these take a location parameter, which was not validated, i.e you could read/write to any location the solr user can access.

## References
- https://lists.apache.org/thread.html/r1d4a247329a8478073163567bbc8c8cb6b49c6bfc2bf58153a857af1%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rbcd9dff009ed19ffcc2b09784595fc1098fc802a5472f81795f893be%40%3Ccommits.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rc400db37710ee79378b6c52de3640493ff538c2beb41cefdbbdf2ab8%40%3Ccommits.submarine.apache.org%3E
- https://lists.apache.org/thread.html/rf54e7912b7d2b72c63ec54a7afa4adcbf16268dcc63253767dd67d60%40%3Cgeneral.lucene.apache.org%3E
- https://nvd.nist.gov/vuln/detail/CVE-2020-13941
