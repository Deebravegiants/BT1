# [H] Fedify has an LD-Signature Bypass via JSON-LD Named-Graph Restructuring

## Summary
Severity: High
Advisory: GHSA-9rfg-v8g9-9367
CVE: CVE-2026-42462
CWE: CWE-1289, CWE-180, CWE-347, CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-9rfg-v8g9-9367
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=2.2.0 <2.2.3
- npm: `@fedify/fedify` — affected >=2.1.0 <2.1.14
- npm: `@fedify/fedify` — affected >=2.0.0 <2.0.18
- npm: `@fedify/fedify` — affected >=1.10.0 <1.10.10
- npm: `@fedify/fedify` — affected >=0 <1.9.11

## Details
As told on Discord earlier, multiple projects are affected, and we would like to coordinate. For now, we are aiming at a May 6th release date, but this is not set in stone yet.

### Summary

An attacker can make use of JSON-LD features to restructure a JSON-LD document that would change how Fedify interprets it without changing its Linked Data Signature, allowing them to alter a third-party signed activity they have received.

### Details

The vulnerability essentially boils down to the signature being on the canonical RDF graph representation of the JSON-LD document, and JSON-LD offering many ways to represent the same graph.

One of the issues is that by taking a signed `Activity` with an embedded `object`, an attacker can move the top-level `Activity` to a `@graph` property and move the activity's `object` to the top-level. Such a transformation preserves the signature and changes how the payload is interpreted by pretty much all ActivityPub implementations, making them process the object and ignore the formely-top-level activity. This can be used when the graph contains an embedded activity. In Mastodon, that is the case of `{ "type": "Undo", "object": { "type": "Announce" } }`, but other implementations may sign other activities that can be exploited in the same way.

The `@reverse` keyword can also be used to change the shape of a JSON-LD document without changing the underlying graph, and could be used in a similar way to reverse an `Activity` and its `object`.

Another problematic feature is `@included`, which can be used to “move” properties outside of the normal tree, effectively making them invisible to most ActivityPub implementations, while, again, preserving the signature. This allows removing statuses or actor properties once a signed `Create` or `Update` activity is received.

Given that we have seen no use of `@graph`, `@included` or `@reverse` in ActivityPub payloads and that they are very complex to handle correctly (the only JSON-LD API functions that “normalize” `@included` and `@reverse` are flattening and framing, which both lose the root node), we have decided to reject them, and recommend you do so as well.

Detection of `@graph`, `@included` and `@reverse` should happen after compacting the incoming activity to your context, as aliases can be used for those keywords.

Additionally, after a quick scan of Fedify's source code, I could not verify that JSON-LD documents with a verified Linked Data Signature were compacted against your local JSON-LD context. Not doing that allows an attacker to rename aliases to non-standard names and use non-mapped aliases to replace existing values, while still leaving the signature intact. This allows an attacker to essentially replace arbitrary portions of any signed JSON-LD document and completely forge any activity while still passing verification. A similar issue was fixed in Mastodon a few years ago: https://github.com/mastodon/mastodon/pull/17426.

### Impact

The impact is difficult to assess as this depends on the types of activities that are actually signed and processed in the wild.

The `@included` keyword allows “removing” arbitrary attributes, thus allowing replaying `Create` and `Update` activities while stripping away any attribute, such as content or metadata, which can lead to integrity and availability issues, although confidentiality issues are unlikely.

The `@graph` and `@reverse` keywords allow changing the root activity, which in the case of Mastodon allows sending an `Announce` from a `Undo { Announce }`, but might have wider consequences depending on what various servers sign.

The lack of compacting can allow rewriting any activity arbitrarily, thus leading to major integrity, availability, and possibly confidentiality issues (e.g. by replacing an actor's `inbox`).

## References
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-9rfg-v8g9-9367
- https://nvd.nist.gov/vuln/detail/CVE-2026-42462
- https://github.com/fedify-dev/fedify
- https://github.com/fedify-dev/fedify/releases/tag/2.2.3
