# [H] Authenticated Elasticsearch Painless script execution via Query.search.sort_query on hackerone.com/graphql

## Summary
Severity: High (CVSS 8.8)
Program: HackerOne
Weakness: Code Injection
Reporter: brumbelow
State: resolved
Disclosed: 2026-06-17T14:17:26.678Z
Source: https://hackerone.com/reports/3694007

## Details
**Summary:**
- The `sort_query: String` argument on `Query.search` (`hackerone.com/graphql`) is passed to the downstream Elasticsearch cluster as the raw value of the `sort` parameter, without server-side schema validation, keyword allowlisting, or rejection of scripted sort directives.

- I confirmed per-document Painless script execution by submitting two requests that differ only in the `script.source` field and observing that the script's return value determined document ordering. 

- The first request returned a constant sort key; the second read each document's internal `_seq_no` metadata field and returned it as the sort key. The result sets share zero overlapping documents in the first five positions, and the second request's ordering matches a known ascending-by-`_seq_no` baseline. This difference is only explainable by the Painless script compiling and executing per document against the `doc` context.

All testing was conducted against documents within my own authorization boundary (`NotificationsIndex`, scoped to my own notifications by a server-side user filter). The scripts I supplied did not read any user content, any foreign-tenant data, or any field beyond the `_seq_no` ES-internal metadata field.

**Description:**
- **URL:** `https://hackerone.com/graphql`
- **Method:** `POST`
- **GraphQL field:** `Query.search`
- **Argument:** `sort_query: String`
- **Index tested:** `NotificationsIndex`

The following additional surfaces expose the same `sort_query: String` argument and are likely to share the vulnerability, but were not tested:

- `Query.search` with other `IndexEnum` values (`DuplicateDetectorReportsIndex`, `OpportunitiesIndex`, `CompleteHacktivityReportIndex`, `StoredQueriesIndex`)
- `Organization.findings_search.sort_query: String`

## Steps To Reproduce

### Environment assumptions

All PoC commands assume the same browser session as the production frontend:

```bash
# /tmp/h1.headers contents:
#   accept: */*
#   content-type: application/json
#   origin: https://hackerone.com
#   referer: https://hackerone.com/notifications
#   user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36
#   x-csrf-token: <session CSRF token>
#   x-product-area: notifications
#   x-product-feature: overview
#
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3694007_
