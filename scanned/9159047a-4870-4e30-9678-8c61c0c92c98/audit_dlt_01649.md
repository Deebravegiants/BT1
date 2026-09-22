# [?] CVE-2022-1650 Exposure of Sensitive Information to an Unauthorized Actor (#2172)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2022-09-06
Source: https://github.com/cosmos/ibc-go/commit/5d5bcb2f99d2c53138bc9f0646cac4f8163220d9
Type: security-commit

## Details
CVE-2022-1650 Exposure of Sensitive Information to an Unauthorized Actor (#2172)

## Describe the bugs: 🐛
A flaw was found in the EventSource NPM Package. The description from the source states the following message: "Exposure of Sensitive Information to an Unauthorized Actor." This flaw allows an attacker to steal the user's credentials and then use the credentials to access the legitimate server. When fetching an url with a link to an external site (Redirect), the users Cookies & Autorisation headers are leaked to the third party application. According to the same-origin-policy, the header should be "sanitized".

**Proof of Concept**
Start a nodejs server (attacker):
```js
    const express = require('express')
    const app = express()

    app.get('/', function (req, res) {
        console.log(req.headers);
        res.status(200).send()
    })

    app.listen(3000)

    console.log('listening on port 3000');
```

**CVE-2022-1650**
`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
GHSA-6h5x-7c5m-7cr7







---

Before we can merge this PR, please make sure that all the following items have been
checked off. If any of the checklist items are not applicable, please leave them but
write a little note why.

- [x] Targeted PR against correct branch (see [CONTRIBUTING.md](https://github.com/cosmos/ibc-go/blob/master/CONTRIBUTING.md#pr-targeting))
- [x] Linked to Github issue with discussion and accepted design OR link to spec that describes this work.
- [x] Code follows the [module structure standards](https://github.com/cosmos/cosmos-sdk/blob/master/docs/building-modules/structure.md).
- [x] Wrote unit and integration [tests](https://github.com/cosmos/ibc-go/blob/master/CONTRIBUTING.md#testing)
- [x] Updated relevant documentation (`docs/`) or specification (`x/<module>/spec/`)
- [x] Added relevant `godoc` [comments](https://blog.golang.org/godoc-documenting-go-code).
- [x] Added a relevant changelog entry to the `Unreleased` section in `CHANGELOG.md`
- [x] Re-reviewed `Files changed` in the Github PR explorer
- [x] Review `Codecov Report` in the comment section below once CI passes

### docs/package-lock.json
```diff
@@ -4826,9 +4826,9 @@
       "integrity": "sha512-mQw+2fkQbALzQ7V0MY0IqdnXNOeTtP4r0lN9z7AAawCXgqea7bDii20AYrIBrFd/Hx0M2Ocz6S111CaFkUcb0Q=="
     },
     "eventsource": {
-      "version": "1.1.0",
-      "resolved": "https://registry.npmjs.org/eventsource/-/eventsource-1.1.0.tgz",
-      "integrity": "sha512-VSJjT5oCNrFvCS6igjzPAt5hBzQ2qPBFIbJ03zLI9SE0mxwZpMw6BfJrbFHm1a141AavMEB8JHmBhWAd66PfCg==",
+      "version": "1.1.2",
+      "resolved": "https://registry.npmjs.org/eventsource/-/eventsource-1.1.2.tgz",
+      "integrity": "sha512-xAH3zWhgO2/3KIniEKYPr8plNSzlGINOUqYj0m0u7AB81iRw8b/3E73W6AuU+6klLbaSFmZnaETQ2lXPfAydrA=="
       "requires": {
         "original": "^1.0.0"
       }
```
