# [C] Command injection in Parse Server through prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-p6h4-93qp-jhcm
CVE: CVE-2022-24760
CWE: CWE-1321, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-p6h4-93qp-jhcm
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.10.7

## Details
### Impact
This is a Remote Code Execution (RCE) vulnerability in Parse Server. This vulnerability affects Parse Server in the default configuration with MongoDB. The main weakness that leads to RCE is the Prototype Pollution vulnerable code in the file `DatabaseController.js`, so it is likely to affect Postgres and any other database backend as well. This vulnerability has been confirmed on Linux (Ubuntu) and Windows.

### Patches
Upgrade to Parse Server >=4.10.7. If you are using a prerelease version of Parse Server 5.0 (alpha, beta) we will publish a timely fix for these. However, as a general reminder we do not consider prerelease versions to be suitable for production deployment.

Note that as part of the fix a new security feature scans for sensitive keywords in request data to prevent JavaScript prototype pollution. If such a keyword is found, the request is rejected with HTTP response code `400` and Parse Error `105` (`INVALID_KEY_NAME`). By default these keywords are: `{_bsontype: "Code"}`, `constructor`, `__proto__`. If you are using any of these keywords in your request data, you can override the default keywords by setting the new Parse Server option `requestKeywordDenylist` to `[]` and specify your own keywords as needed.

### Workarounds
Although the fix is more broad and includes several aspects of the vulnerability, a quick and targeted fix can be achieved by patching the MongoDB Node.js driver and disable BSON code execution. To apply the patch, add the following code to be executed before starting Parse Server, for example in `index.js`.

```
const BSON = require('bson');
 const internalDeserialize = BSON.prototype.deserialize;
 BSON.prototype.deserialize = (buffer, options = Object.create(null), ...others) => {
   if (options.constructor) {
     options = Object.assign(Object.create(null), options);
   }
   return internalDeserialize(buffer, options, ...others);
 };
 const internalDeserializeStream = BSON.prototype.deserializeStream;
 BSON.prototype.deserializeStream = (
   data,
   startIndex,
   numberOfDocuments,
   documents,
   docStartIndex,
   options = Object.create(null),
   ...others
 ) => {
   if (options.constructor) {
     options = Object.assign(Object.create(null), options);
   }
   return internalDeserializeStream(
     data,
     startIndex,
     numberOfDocuments,
     documents,
     docStartIndex,
     options,
     ...others
   );
 };
```

### References
- Original report on [huntr.dev](https://www.huntr.dev/bounties/ac24b343-e7da-4bc7-ab38-4f4f5cc9d099/)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-p6h4-93qp-jhcm
- https://nvd.nist.gov/vuln/detail/CVE-2022-24760
- https://github.com/parse-community/parse-server/commit/886bfd7cac69496e3f73d4bb536f0eec3cba0e4d
- https://github.com/parse-community/parse-server
- https://www.huntr.dev/bounties/ac24b343-e7da-4bc7-ab38-4f4f5cc9d099
