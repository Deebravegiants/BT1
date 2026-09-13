# [H] OpenRefine leaks Google API credentials in releases

## Summary
Severity: High
Advisory: GHSA-3pg4-qwc8-426r
CWE: CWE-522
Ecosystem: Maven
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-3pg4-qwc8-426r
Type: github-advisory

## Affected
- Maven: `org.openrefine:openrefine` — affected >=0 <3.8.3

## Details
### Impact

OpenRefine releases contain Google API authentication keys ("client id" and "client secret") which can be extracted from released artifacts. For instance, download the package for OpenRefine 3.8.2 on linux. It contains the file `openrefine-3.8.2/webapp/extensions/gdata/module/MOD-INF/lib/openrefine-gdata.jar`, which can be extracted.
This archive then contains the file `com/google/refine/extension/gdata/GoogleAPIExtension.java`, which contains the following lines:

```java
    // For a production release, the second parameter (default value) can be set
    // for the following three properties (client_id, client_secret, and API key) to
    // the production values from the Google API console
    private static final String CLIENT_ID = System.getProperty("ext.gdata.clientid", new String(Base64.getDecoder().decode("ODk1NTU1ODQzNjMwLWhkZWwyN3NxMDM5ZjFwMmZ0aGE2M2VvcWFpY2JwamZoLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29t")));
    private static final String CLIENT_SECRET = System.getProperty("ext.gdata.clientsecret", new String(Base64.getDecoder().decode("R2V2TnZiTnA2a3IxeDd5c3VZNENmYlNo")));
```

The Base64 encoding can then be decoded to obtain the client id and client secret.
Those credentials can then be used by other applications to request access to Google accounts, pretending they are OpenRefine. This assumes that they also get access to the user access tokens, which this vulnerability doesn't expose by itself.

### Patches

The bundled credentials should be revoked.

### Workarounds

Users should revoke access to their Google account if they have connected it to OpenRefine.

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-3pg4-qwc8-426r
- https://github.com/OpenRefine/OpenRefine/commit/07dd61e00bb7f472ddcb243631299fba95ad90dd
- https://github.com/OpenRefine/OpenRefine
