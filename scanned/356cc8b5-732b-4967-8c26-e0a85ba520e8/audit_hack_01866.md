# [H] Superfluous Permission `endowment:network-access`

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The snap requests permission `endowment:network-access` to interact with external entities over HTTP/fetch. While the sandbox/demo dapp may use the fetch API in its context as a web app, the requested permission is only relevant for the snap and the snap never calls the `fetch()` API. Hence, the permission is requested but never used.

Requesting more permissions than necessary should always be avoided following the principle of least privilege.

#### Examples


**packages/snap/snap.manifest.json:L69**
```solidity
"endowment:network-access": {},
```

#### Recommendation

Remove superfluous permissions.
