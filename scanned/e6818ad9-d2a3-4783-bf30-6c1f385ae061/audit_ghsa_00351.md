# [H] Private Data Disclosure in express-restify-mongoose

## Summary
Severity: High
Advisory: GHSA-cgjx-mwpx-47jv
CVE: CVE-2016-10533
CWE: CWE-200
Ecosystem: npm
Published: 2018-10-23
Source: https://github.com/advisories/GHSA-cgjx-mwpx-47jv
Type: github-advisory

## Affected
- npm: `express-restify-mongoose` — affected >=3.0.0 <3.1.0
- npm: `express-restify-mongoose` — affected >=0 <2.5.0

## Details
Affected versions of `express-restify-mongoose` are susceptible to an information leakage vulnerability which may allow an attacker to access fields on a model even if those fields are marked as private.


## Proof of Concept

If you have a user model that you want to protect, such as the following User model:
```
const User = mongoose.model('User', new mongoose.Schema({
    name: String,
    password: String,
}));
```

You would normally do something such as:
```
restify.serve(router, User, {
    private: ['password'], // Set the password part of User as private, so outside people can't read it
})
```

This would hide the password field from people that send your application a `GET /User` and `GET /User/some-user-id` request. 

A malicious user can go to your application and send a request for `GET /User?distinct=password` and get all the passwords for all the users in the database, despite the field being set to private. This could be used for other private data, if the malicious user knew what was set as private for specific routes.


## Recommendation

Version 2.x: Update to version 2.5.0 or later.
Version 3.x: Update to version 3.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10533
- https://github.com/florianholzapfel/express-restify-mongoose/issues/252
- https://github.com/florianholzapfel/express-restify-mongoose/pull/253
- https://github.com/florianholzapfel/express-restify-mongoose/commit/23ccb247d0074bfaca6737cdff52d89c6d6e4a7c
- https://github.com/florianholzapfel/express-restify-mongoose/commit/746defcd808e2ed1e8931dc36702b25b7db0e94b
- https://github.com/advisories/GHSA-cgjx-mwpx-47jv
- https://www.npmjs.com/advisories/92
