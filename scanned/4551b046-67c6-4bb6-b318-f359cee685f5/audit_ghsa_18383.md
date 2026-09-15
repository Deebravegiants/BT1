# [H] DynamicPageList3 vulnerability exposes hidden/suppressed usernames

## Summary
Severity: High
Advisory: GHSA-7pgw-q3qp-6pgq
CVE: CVE-2025-53625
CWE: CWE-359
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-7pgw-q3qp-6pgq
Type: github-advisory

## Affected
- Packagist: `universal-omega/dynamic-page-list3` — affected >=0 <3.6.4

## Details
### Summary
Several `#dpl` parameters can leak usernames that have been hidden using revision deletion, suppression, or the `hideuser` block flag.

### Details
The parameters `adduser`, `addauthor`, and `addlasteditor` output the page creator or last editor using the `%USER%` placeholder. These display the actual username, even when that name has been hidden using revision deletion, suppression (oversight), or `hideuser`.

The `%CONTRIBUTOR%` placeholder, used with `addcontribution`, behaves similarly and also reveals hidden usernames.

In addition, the following parameters can expose suppressed usernames when combined with `%USER%` or similar output placeholders:
- `lastrevisionbefore`
- `allrevisionsbefore`
- `firstrevisionsince`
- `allrevisionssince`

These parameters reference specific revisions and allow output of user-related metadata. If a username has been hidden from those revisions, it may still appear in the output.

Further, the parameters `createdby`, `notcreatedby`, `modifiedby`, `notmodifiedby`, `lastmodifiedby`, and `notlastmodifiedby` accept usernames as input. When the correct (suppressed) username is used, the query may return matching pages or edits. This can reveal the presence and association of a hidden identity, even if not displayed directly. However, this is a more indirect exposure than the output parameters mentioned above.

### Proof of Concept

1. Create a page while logged in as a user.
2. Revision delete or suppress the username from the page history.
3. Use a DPL query with one of the affected parameters.
4. The output reveals the hidden username.

#### Example

The following query reveals the suppressed username `Example user`:

```wikitext
{{#dpl:
| title = File:Example.png
| addauthor = true
| format = ,%USER%,,
}}
```

Similar behavior occurs using parameters like `lastrevisionbefore` with `%USER%` in the `format` string.

### Impact
This issue causes the exposure of usernames that were intentionally hidden by administrators. It directly undermines revision deletion, user suppression, and block-related privacy measures. In some cases, usernames can be revealed both directly through output and indirectly through query behavior.

## References
- https://github.com/Universal-Omega/DynamicPageList3/security/advisories/GHSA-7pgw-q3qp-6pgq
- https://nvd.nist.gov/vuln/detail/CVE-2025-53625
- https://github.com/Universal-Omega/DynamicPageList3/commit/a3dae0c89fb4214390c29ceffa23bbe2099986d6
- https://github.com/Universal-Omega/DynamicPageList3
