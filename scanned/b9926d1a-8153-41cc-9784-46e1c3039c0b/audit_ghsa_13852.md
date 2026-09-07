# [C] LiteDB may deserialize bad JSON on object type using _type

## Summary
Severity: Critical
Advisory: GHSA-3x49-g6rc-c284
CVE: CVE-2022-23535
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-3x49-g6rc-c284
Type: github-advisory

## Affected
- NuGet: `LiteDB` — affected >=0 <5.0.13

## Details
### Impact
LiteDB use a special field in JSON documents to cast diferent types from `BsonDocument` do POCO classes. When instance of an object are not the same of class, `BsonMapper` use a special field `_type` string info with full class name with assembly to be loaded and fit in your model.
If your end-user can send to your app a plain JSON string, deserialization can load an unsafe  object to fit in your model.

### Patches
Version >= 5.0.13 add some basic fixes to avoid this, but is not 100% guaranteed when using `Object` type
Next major version will contains a allow-list to select what king of Assembly can be loaded

### Workarounds
- Avoid users send to your app a JSON string to be direct insert/update into database
- Avoid use classes with `Object` type - try use an interface when possible

If your app send a plain JSON string to be insert/update into database, prefer this:
```
// Bad
public class Customer {
    public int Id { get; set; }
    public string Name { get; set; }
    public Object AnyData { get; set; } // <= Avoid use `Object` base type
}

// Good
public class Customer {
    public int Id { get; set; }
    public string Name { get; set; }
    public IDictionary<string, string> AnyData { get; set; } // Will accept only key/value strings
}

```

### References
See this workaround fix on this commit:

https://github.com/mbdavid/LiteDB/commit/4382ff4dd0dd8b8b16a4e37dfd29727c5f70f93f

## References
- https://github.com/mbdavid/LiteDB/security/advisories/GHSA-3x49-g6rc-c284
- https://nvd.nist.gov/vuln/detail/CVE-2022-23535
- https://github.com/mbdavid/LiteDB/commit/4382ff4dd0dd8b8b16a4e37dfd29727c5f70f93f
- https://github.com/mbdavid/LiteDB/commit/d72c6774e6a13de2cfcd7d477d3575efeb75c8f2
- https://github.com/mbdavid/LiteDB
- https://github.com/mbdavid/LiteDB/releases/tag/v5.0.13
