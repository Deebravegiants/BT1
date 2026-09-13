# [H] Graylog vulnerable to instantiation of arbitrary classes triggered by API request

## Summary
Severity: High
Advisory: GHSA-p6gg-5hf4-4rgj
CVE: CVE-2024-24824
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-p6gg-5hf4-4rgj
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=2.0.0 <5.1.11
- Maven: `org.graylog2:graylog2-server` — affected >=5.2.0-alpha.1 <5.2.4

## Details
### Summary

Arbitrary classes can be loaded and instantiated using a HTTP PUT request to the `/api/system/cluster_config/` endpoint.

### Details

Graylog's cluster config system uses fully qualified class names as config keys. To validate the existence of the requested class before using them, Graylog loads the class using the class loader. 

https://github.com/Graylog2/graylog2-server/blob/e458db8bf4f789d4d19f1b37f0263f910c8d036c/graylog2-server/src/main/java/org/graylog2/rest/resources/system/ClusterConfigResource.java#L208-L214


### PoC
A request of the following form will output the content of the `/etc/passwd` file:

```
curl -u admin:<admin-password> -X PUT http://localhost:9000/api/system/cluster_config/java.io.File \
    -H "Content-Type: application/json" \
    -H "X-Requested-By: poc" \
    -d '"/etc/passwd"'
```

To perform the request, authorization is required. Only users posessing the `clusterconfigentry:create` and `clusterconfigentry:edit` permissions are allowed to do so. These permissions are usually only granted to `Admin` users.

### Impact

If a user with the appropriate permissions performs the request, arbitrary classes with 1-arg String constructors can be instantiated. 

This will execute arbitrary code that is run during class instantiation.

In the specific use case of `java.io.File`, the behaviour of the internal web-server stack will lead to information exposure by including the entire file content in the response to the REST request.

### Credits

Analysis provided by Fabian Yamaguchi - Whirly Labs (Pty) Ltd

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-p6gg-5hf4-4rgj
- https://nvd.nist.gov/vuln/detail/CVE-2024-24824
- https://github.com/Graylog2/graylog2-server/commit/75ef2b8d60e7d67f859b79fe712c8ae7b2e861d8
- https://github.com/Graylog2/graylog2-server/commit/7f8ef7fa8edf493106d5ef6f777d4da02c5194d9
- https://github.com/Graylog2/graylog2-server
- https://github.com/Graylog2/graylog2-server/blob/e458db8bf4f789d4d19f1b37f0263f910c8d036c/graylog2-server/src/main/java/org/graylog2/rest/resources/system/ClusterConfigResource.java#L208-L214
