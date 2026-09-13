# [M] ApostropheCMS: Information Disclosure via choices/counts Query Parameters Bypassing publicApiProjection Field Restrictions

## Summary
Severity: Medium
Advisory: GHSA-c276-fj82-f2pq
CVE: CVE-2026-39857
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-c276-fj82-f2pq
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <4.29.0

## Details
## Summary

The `choices` and `counts` query parameters in the Apostrophe CMS REST API allow unauthenticated users to extract distinct field values for any schema field that has a registered query builder, completely bypassing `publicApiProjection` restrictions that are intended to limit which fields are exposed publicly. Fields protected by `viewPermission` are similarly exposed.

## Details

When a piece type configures `publicApiProjection` to enable public API access while restricting visible fields, the restriction is enforced via a MongoDB projection on the main query (piece-type/index.js:1130-1134). However, the `choices` and `counts` query builders bypass this protection through a separate code path.

The vulnerable flow:

1. `getRestQuery` at piece-type/index.js:1120 calls `applyBuildersSafely(req.query)` (line 1122), which processes query parameters including `choices` and `counts` since both have `launder` methods (doc-type/index.js:2627-2628 and 2675-2676).

2. The `publicApiProjection` is applied afterward (line 1130-1134) as a MongoDB projection on the main query.

3. During query execution, the `choices` builder's `after` handler (doc-type/index.js:2636-2668) iterates over requested field names. The only validation is:
   - The field has a registered builder (`_.has(query.builders, filter)` at line 2651)
   - The builder has a `launder` method (line 2656)

   All schema field types (string, integer, float, select, boolean, date, slug, relationship) register query builders with `launder` methods via `addQueryBuilder` in `addFieldTypes.js`.

4. `toChoices` (line 2661) calls the field's `choices` function, which typically calls `sortedDistinct` → `toDistinct`. The `toDistinct` method (doc-type/index.js:2811) executes `db.distinct(property, criteria)` — a MongoDB operation that returns all distinct values for the given property matching the criteria. **MongoDB's `distinct` operation does not respect projections**; it operates directly on the specified field regardless of any projection set on the query.

5. The results are stored via `query.set('choicesResults', choices)` (line 2666) and returned directly in the API response at piece-type/index.js:292-296 without any filtering against `publicApiProjection` or `removeForbiddenFields`.

The same bypass applies to `viewPermission`-protected fields: `removeForbiddenFields` (doc-type/index.js:1585-1611) only processes document results from `toArray()`, not the separate choices/counts data.

The page REST API has the same issue at page/index.js:371-376.

## PoC

```bash
# Prerequisites:
# - An Apostrophe 4.x instance with a piece type configured with publicApiProjection
# - Example: an 'article' piece type with:
#   publicApiProjection: { title: 1, slug: 1, _url: 1 }
#   and additional schema fields like 'status' (select), 'priority' (integer),
#   or 'internalNotes' (string) NOT in the projection

# 1. Verify normal API access only returns projected fields
curl -s 'http://localhost:3000/api/v1/article' | python3 -m json.tool
# Response results contain only: title, slug, _url (as configured)

# 2. Extract distinct values of a non-projected field via choices
curl -s 'http://localhost:3000/api/v1/article?choices=status' | python3 -m json.tool
# Response includes:
# "choices": {"status": [{"value": "draft", "label": "draft"}, {"value": "published", "label": "published"}, ...]}

# 3. Extract distinct values with document counts via counts
curl -s 'http://localhost:3000/api/v1/article?counts=priority' | python3 -m json.tool
# Response includes:
# "counts": {"priority": [{"value": 1, "label": "1", "count": 15}, {"value": 2, "label": "2", "count": 8}, ...]}

# 4. Multiple fields can be extracted at once
curl -s 'http://localhost:3000/api/v1/article?choices=status,priority,internalNotes'
```

## Impact

- **Distinct field values leaked**: An unauthenticated attacker can extract all distinct values of any schema field on any piece type that has `publicApiProjection` configured, even when those fields are explicitly excluded from the projection.
- **Field types affected**: All field types that register query builders: string, slug, integer, float, select, boolean, date, and relationship fields.
- **Count disclosure**: The `counts` variant additionally reveals how many documents have each distinct value, providing statistical information about the dataset.
- **viewPermission bypass**: Fields protected with `viewPermission` (intended for role-based field access) are also exposed via this path.
- **Both APIs affected**: The piece-type REST API (piece-type/index.js:292-296) and page REST API (page/index.js:371-376) are both vulnerable.
- **Real-world impact**: If a CMS stores sensitive data in schema fields (e.g., internal status values, priority levels, internal categories, user-facing content marked as restricted), all distinct values are extractable by any unauthenticated visitor.

## Recommended Fix

In the `choices` builder's `after` handler (doc-type/index.js:2636-2668), add validation to skip fields not permitted by `publicApiProjection` and `viewPermission`:

```javascript
// doc-type/index.js, in the choices builder's after handler (line 2644 area)
for (const filter of filters) {
  if (!_.has(query.builders, filter)) {
    continue;
  }
  if (!query.builders[filter].launder) {
    continue;
  }

  // NEW: Enforce publicApiProjection restrictions on choices/counts
  const publicApiProjection = query.get('project');
  if (publicApiProjection && !publicApiProjection[filter]) {
    continue;
  }

  // NEW: Enforce viewPermission field restrictions
  const field = self.schema.find(f => f.name === filter);
  if (field && field.viewPermission &&
      !self.apos.permission.can(query.req, field.viewPermission.action, field.viewPermission.type)) {
    continue;
  }

  const _query = baseQuery.clone();
  _query[filter](null);
  choices[filter] = await _query.toChoices(filter, { counts: query.get('counts') });
}
```

Additionally, apply the same fix in the page REST API handler (page/index.js) for consistency.

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-c276-fj82-f2pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39857
- https://github.com/apostrophecms/apostrophe/commit/6c2b548dec2e3f7a82e8e16736603f4cd17525aa
- https://github.com/apostrophecms/apostrophe
