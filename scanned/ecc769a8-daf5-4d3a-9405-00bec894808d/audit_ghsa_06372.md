# [H] GeoLens: Cross-dataset authorization bypass discloses private dataset metadata, schema, sample values, table rows, and raster/vector tile data

## Summary
Severity: High
Advisory: GHSA-p23g-mvhj-jh3j
CVE: CVE-2026-55178
CWE: CWE-200, CWE-639, CWE-862
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-p23g-mvhj-jh3j
Type: github-advisory

## Affected
- npm: `@geolens/sdk` — affected >=0 <1.2.3
- PyPI: `geolens-cli` — affected >=0 <1.2.3
- PyPI: `geolens` — affected >=0 <1.2.3

## Details
### Summary

Multiple GeoLens read/link endpoints authorized only the resource named in the
request URL (a map, a VRT, a source dataset, an AI request) and failed to
re-authorize a **second, caller-influenced dataset** that the request reached
through a relationship, layer reference, mosaic source, or request body. This
"authorize the URL resource, read a *different* dataset un-re-authorized"
pattern let callers read data from datasets they have no access to.

The most severe instances require **no authentication at all** (anonymous,
network-only). Others require only the **default `editor` role** that any
self-service signup / upload user receives.

All issues are fixed in **1.2.3**. There is no complete configuration
workaround — upgrading is the only full remediation.

### Impact

Depending on the endpoint, an attacker can read, for datasets they cannot
otherwise access:

- the dataset's **vector tile data** (actual feature geometries/attributes),
- the dataset's **raster pixels**,
- backing-table **rows**,
- and **metadata** — table name, column schema, feature count, extent, source
  URL/filename, contacts, and **sampled row values**.

### Affected versions

All versions **prior to 1.2.3** (includes the published 1.0.0, 1.2.0, and
1.2.2 releases and their PyPI/npm/GHCR artifacts). Fixed in **1.2.3**.

### Findings

**1. Anonymous metadata + private vector-tile disclosure via public maps (PR #235)**
`GET /maps/{id}` and `GET /maps/{id}/style.json` authorized the map but not
each layer's backing dataset. A public map that references a private dataset
leaked that dataset's table name, column schema, feature count, extent, and
sampled values to anonymous callers. `style.json` additionally returned a
vector-tile URL carrying an HMAC signature bound to **neither user nor map**,
which the tile endpoint accepts for non-public datasets with no user check —
so the signature is **replayable** to read the private dataset's actual vector
tiles. *(Anonymous · High)*

**2. Anonymous private-row disclosure via dataset relationships (PR #234)**
The dataset FK-relationship APIs authorized only the source dataset from the
URL, never the relationship target. A public dataset with a relationship to a
private dataset let an anonymous caller enumerate the relationship (obtaining
the private target's id/title and the relationship id) and then call the
related-record endpoint to read **rows from the private target's backing
table**. *(Anonymous · High)*

**3. Anonymous metadata disclosure via OGC `externalId` lookup (PR #236)**
`GET /collections/datasets/items?externalId=<uuid>` resolved the dataset by id
and returned the full OGC catalog record (title, summary, bbox, keywords,
contacts, distributions, source org) with **no visibility check** — the user
was never threaded into the lookup. An anonymous caller could read any
private, restricted, or unpublished dataset's metadata by UUID. *(Anonymous ·
High)*

**4. Cross-tenant raster pixel disclosure via VRT mosaics — SEC-C (PR #237)**
An authenticated user with the default `editor` upload permission could mosaic
another user's **private raster** into a VRT they own, then read the victim's
**pixels** back through raster tile / quicklook / COG endpoints that authorize
only the attacker-owned VRT. VRT member pixels are compiled into one served
asset and cannot be filtered at read time, so the fix authorizes every source
dataset at write/link time. *(Authenticated `editor` · High)*

**5. Cross-tenant metadata/sample-data disclosure via AI metadata endpoints — SEC-D (PR #238)**
The `POST /ai/metadata/{summary,keywords,lineage,quality-statement}` endpoints
were gated only by the `use_ai_chat` permission (held by the default `editor`
role). The attacker-controlled `dataset_id` in the request body flowed into the
LLM prompt context with no visibility filter, rendering **any** dataset's
title, summary, source URL, filename, column schema, and **sample values** into
the response. *(Authenticated `editor` · High)*

**6. Residual VRT member disclosure for legacy links — SEC-E (PR #237)**
Link-time authorization (finding 4) does not re-authorize pre-existing
`vrt_source_links`, so legacy or authorization-drift links still leaked member
metadata and health via the VRT source-listing/status endpoints until a
per-member read filter was added. *(Medium)*

### Patches

Fixed in **1.2.3** by, in order:

- `31a103b9` — fix(catalog): authorize relationship targets in related-record endpoints (#234)
- `01bc87da` — fix(maps): re-authorize each layer's dataset on anonymous map read endpoints (#235)
- `407c0688` — fix(ogc): enforce dataset visibility on the externalId OGC item lookup (#236)
- `2c031da8` — fix(vrt): authorize VRT source datasets at link time + filter unauthorized members on read (#237)
- `07dfb1c6` — fix(ai): authorize the requested dataset on AI metadata endpoints (#238)

The fixes follow the codebase's established per-dataset re-authorization pattern
(`can_access_dataset` / `check_dataset_access_or_anonymous`), filtering at read
time and authorizing cross-dataset references at link/write time.

### Workarounds

There is **no complete configuration workaround**; the anonymous findings
require only network access to the API. Operators who cannot upgrade
immediately should restrict network exposure of the API and avoid co-locating
private datasets with public maps/relationships, but **upgrading to 1.2.3 is
the only full remediation**.

### Remediation

Upgrade to GeoLens **1.2.3**:
- Container images: `ghcr.io/geolens-io/geolens-api:1.2.3` (+ worker/frontend)
- Python SDK: `geolens==1.2.3` · CLI: `geolens-cli==1.2.3` · npm: `@geolens/sdk@1.2.3`

## References
- https://github.com/geolens-io/geolens/security/advisories/GHSA-p23g-mvhj-jh3j
- https://github.com/geolens-io/geolens/pull/234
- https://github.com/geolens-io/geolens/pull/235
- https://github.com/geolens-io/geolens/pull/236
- https://github.com/geolens-io/geolens/pull/237
- https://github.com/geolens-io/geolens/pull/238
- https://github.com/geolens-io/geolens
