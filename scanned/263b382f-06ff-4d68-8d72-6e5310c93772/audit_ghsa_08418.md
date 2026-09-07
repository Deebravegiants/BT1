# [H] Mongoose's Improper Sanitization of $nor in sanitizeFilter May Allow NoSQL Injection

## Summary
Severity: High
Advisory: GHSA-wpg9-53fq-2r8h
CVE: CVE-2026-42334
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-wpg9-53fq-2r8h
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=0 <6.13.9
- npm: `mongoose` — affected >=7.0.0 <7.8.9
- npm: `mongoose` — affected >=8.0.0 <8.22.1
- npm: `mongoose` — affected >=9.0.0 <9.1.6

## Details
### Impact

This vulnerability allows bypassing Mongoose’s sanitizeFilter query sanitization mechanism via the `$nor` operator.

When sanitizeFilter is enabled, Mongoose wraps query operators in `$eq` to neutralize them. However, prior to the fix, `$nor` was not included in the set of logical operators that are recursively sanitized. Because `$nor` accepts an array (like `$and` and `$or`), and arrays do not trigger `hasDollarKeys()`, malicious operators such as `$ne`, `$gt`, or `$regex` could be injected inside a `$nor` clause without being sanitized.

This may lead to:

- Authentication bypass
- Unauthorized data access
- Data exfiltration

**Affected users:**

Applications that:

- Explicitly enable sanitizeFilter
- Pass unsanitized user-controlled input directly into query methods (e.g., `Model.findOne(req.body)`) and rely on `sanitizeFilter` to strip out query selectors

Applications that validate input schemas, whitelist fields, or avoid passing raw request bodies into queries are not affected. For example, `Model.findOne({ user: req.body.user, pwd: req.body.pwd })` is not affected.

### Patches

Patches have been released for all supported Mongoose release lines:

- `^6.13.9`
- `^7.8.9`
- `^8.22.1`
- `^9.1.6`   

### Workarounds

Delete `$nor` keys, use an additional schema validation library, or write middleware to strip out `$nor` from query filters.

### Resources

sanitizeFilter documentation: https://mongoosejs.com/docs/api/mongoose.html#Mongoose.prototype.sanitizeFilter()

Original blog post on sanitizeFilter: https://thecodebarbarian.com/whats-new-in-mongoose-6-sanitizefilter.html

## References
- https://github.com/Automattic/mongoose/security/advisories/GHSA-wpg9-53fq-2r8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42334
- https://github.com/Automattic/mongoose
- https://mongoosejs.com/docs/api/mongoose.html#Mongoose.prototype.sanitizeFilter()
- https://thecodebarbarian.com/whats-new-in-mongoose-6-sanitizefilter.html
