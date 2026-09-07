# [M] Unwanted access to the entire file system vulnerability due to a missing check in `staticFiles` HTTP handler

## Summary
Severity: Medium
Advisory: GHSA-j2wh-wrv3-4x4g
CVE: CVE-2025-27098
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-j2wh-wrv3-4x4g
Type: github-advisory

## Affected
- npm: `@graphql-mesh/cli` — affected >=0.78.0 <0.82.22
- npm: `@graphql-mesh/http` — affected >=0 <0.3.19

## Details
### Summary
Missing check vulnerability in the static file handler allows any client to access the files in the server's file system

### Details
When `staticFiles` is set in the `serve` settings in the configuration file, the following handler doesn't check if `absolutePath` is still under the directory provided as `staticFiles`;

```ts
  if (staticFiles) {
    router.get('/:relativePath+', async request => {
      let { relativePath } = request.params;
      if (!relativePath) {
        relativePath = 'index.html';
      }
      const absolutePath = path.join(baseDir, staticFiles, relativePath);
      if (absolutePath.includes(staticFiles) && (await pathExists(absolutePath))) {
        const readStream = fs.createReadStream(absolutePath);
        return new Response(readStream as any, {
          status: 200,
        });
      }
      return undefined;
    });
 ```

### Example scenario
To reproduce it, set `staticFiles` to the relative path of a directory in `.meshrc.yml`;

```yml
serve:
   staticFiles: ./public
```

Then start the server with `mesh dev`, and browse to `/..%2fpackage.json` then you will see the content of `package.json`. You can even go deeper to see sensitive data; `/..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fetc/passwd`

### Impact and solution
If `staticFiles` is set under `serve` in the configuration file. you have two options to fix vulnerability;

- Update `@graphql-mesh/cli` to a version higher than `0.82.21`, and if you use `@graphql-mesh/http`, update it to a version higher than `0.3.18`
- Remove `staticFiles` option from the configuration, and use other solutions to serve static files.

### Credits
Thanks [alanwillms@gmail.com](mailto:alanwillms@gmail.com) for reporting this vulnerability with details

## References
- https://github.com/Urigo/graphql-mesh/security/advisories/GHSA-j2wh-wrv3-4x4g
- https://github.com/ardatan/graphql-mesh/security/advisories/GHSA-j2wh-wrv3-4x4g
- https://nvd.nist.gov/vuln/detail/CVE-2025-27098
- https://github.com/Urigo/graphql-mesh/commit/95d93e7c140c2995b37e9d822aa3fe4e24ed2e78
- https://github.com/Urigo/graphql-mesh
