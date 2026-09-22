# [M] ApostropheCMS: publicApiProjection Bypass via project Query Builder in Piece-Type REST API

## Summary
Severity: Medium
Advisory: GHSA-xhq9-58fw-859p
CVE: CVE-2026-33888
CWE: CWE-200, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xhq9-58fw-859p
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <4.29.0

## Details
## Summary

The `getRestQuery` method in the `@apostrophecms/piece-type` module checks whether a MongoDB projection has already been set before applying the admin-configured `publicApiProjection`. An unauthenticated attacker can supply a `project` query parameter in the REST API request to pre-populate the projection state, causing the security-enforced `publicApiProjection` to be skipped entirely. This allows disclosure of fields that the site administrator explicitly restricted from public access.

## Details

When an unauthenticated user queries the piece-type REST API, the `getRestQuery` method processes the request at `modules/@apostrophecms/piece-type/index.js:1120`:

```javascript
// piece-type/index.js:1120-1137
getRestQuery(req, omitPermissionCheck = false) {
  const query = self.find(req).attachments(true);
  query.applyBuildersSafely(req.query);          // [1] attacker input applied first
  if (!omitPermissionCheck && !self.canAccessApi(req)) {
    if (!self.options.publicApiProjection) {
      query.and({
        _id: null
      });
    } else if (!query.state.project) {            // [2] checks if projection already set
      query.project({
        ...self.options.publicApiProjection,
        cacheInvalidatedAt: 1
      });
    }
  }
  return query;
},
```

At **[1]**, `applyBuildersSafely` iterates over all query string parameters and invokes their corresponding builder methods. The `project` builder exists in `@apostrophecms/doc-type` with a `launder` method (`doc-type/index.js:1876`) that sanitizes values to booleans:

```javascript
// doc-type/index.js:1875-1889
project: {
  launder (p) {
    if (!p || typeof p !== 'object' || Array.isArray(p)) {
      return {};
    }
    const projection = Object.entries(p).reduce((acc, [ key, val ]) => {
      return {
        ...acc,
        [key]: self.apos.launder.boolean(val)
      };
    }, {});
    return projection;
  },
```

When a request includes `?project[someField]=1`, the builder sets `query.state.project` to `{someField: true}`. At **[2]**, the conditional `!query.state.project` evaluates to `false` because the state is already populated, so the `publicApiProjection` is never applied.

For comparison, the `@apostrophecms/page` module's equivalent method (`page/index.js:2953`) unconditionally applies the projection:

```javascript
// page/index.js:2953-2958
} else {
  query.project({
    ...self.options.publicApiProjection,
    cacheInvalidatedAt: 1
  });
}
```

## PoC

**Prerequisites:** An ApostropheCMS 4.x instance with a piece-type (e.g., `article`) that has `publicApiProjection` configured to restrict fields. For example:

```javascript
// modules/article/index.js
module.exports = {
  extend: '@apostrophecms/piece-type',
  options: {
    publicApiProjection: {
      title: 1,
      _url: 1
    }
  }
};
```

**Step 1:** Normal request — observe restricted fields are hidden:

```bash
curl 'http://localhost:3000/api/v1/article'
```

Response returns only `title` and `_url` fields per the configured projection.

**Step 2:** Bypass projection by supplying `project` query parameter:

```bash
curl 'http://localhost:3000/api/v1/article?project[internalNotes]=1&project[title]=1&project[slug]=1&project[createdAt]=1'
```

Response now includes `internalNotes`, `slug`, `createdAt`, and any other requested fields — bypassing the admin-configured `publicApiProjection` restriction.

**Step 3:** Request all default fields by projecting inclusion of sensitive fields:

```bash
curl 'http://localhost:3000/api/v1/article?project[_id]=1&project[title]=1&project[slug]=1&project[visibility]=1&project[type]=1&project[createdAt]=1&project[updatedAt]=1'
```

All requested fields are returned, confirming the `publicApiProjection` is fully bypassed.

## Impact

- **Information Disclosure:** An unauthenticated attacker can read any field on documents that are already publicly queryable, bypassing administrator-configured field restrictions. This may expose internal notes, draft content, metadata, or other sensitive fields the administrator intentionally hid from the public API.
- **Scope:** Affects all piece-type modules with `publicApiProjection` configured. The attacker cannot access documents they wouldn't otherwise be able to query (document-level permissions still apply), but they can read any field on accessible documents.
- **Exploitability:** Trivial — requires only appending query parameters to a public URL. No authentication, special tools, or chaining required.

## Recommended Fix

Remove the conditional check on `query.state.project` in `piece-type/index.js`, matching the page module's unconditional behavior. The admin-configured `publicApiProjection` should always override any user-supplied projection for unauthenticated users:

```javascript
// modules/@apostrophecms/piece-type/index.js:1123-1134
// BEFORE (vulnerable):
if (!omitPermissionCheck && !self.canAccessApi(req)) {
  if (!self.options.publicApiProjection) {
    query.and({
      _id: null
    });
  } else if (!query.state.project) {
    query.project({
      ...self.options.publicApiProjection,
      cacheInvalidatedAt: 1
    });
  }
}

// AFTER (fixed):
if (!omitPermissionCheck && !self.canAccessApi(req)) {
  if (!self.options.publicApiProjection) {
    query.and({
      _id: null
    });
  } else {
    query.project({
      ...self.options.publicApiProjection,
      cacheInvalidatedAt: 1
    });
  }
}
```

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-xhq9-58fw-859p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33888
- https://github.com/apostrophecms/apostrophe/commit/00d472804bb622df36a761b6f2cf2b33b2d4ce80
- https://github.com/apostrophecms/apostrophe/commit/6c2b548dec2e3f7a82e8e16736603f4cd17525aa
- https://github.com/apostrophecms/apostrophe
