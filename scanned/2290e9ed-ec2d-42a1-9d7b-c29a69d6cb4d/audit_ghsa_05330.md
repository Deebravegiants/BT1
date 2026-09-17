# [M] YARD static cache reads raw traversal paths before router sanitization

## Summary
Severity: Medium
Advisory: GHSA-pxcc-8665-phx8
CVE: CVE-2026-49342
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-pxcc-8665-phx8
Type: github-advisory

## Affected
- RubyGems: `yard` — affected >=0 <0.9.44

## Details
### Summary
YARD's static cache lookup reads a request path before the router's path cleanup runs. When a server is configured with a document root, a traversal path such as `/../yard-cache-secret.html` is joined against that root and can return a readable sibling `.html` file outside the intended static tree. 

The potential security risk seems low, as only html-ending files can be read, but still the risk of reading arbitrary html files is a confiendtiality issue in itself, which is why we decided to report. Please let us know if this is out of your project's scope.

### Details
The `--docroot` CLI option stores the configured directory in `server_options[:DocumentRoot]` at `lib/yard/cli/server.rb:198`, and adapter initialization copies that value into `adapter.document_root` at `lib/yard/server/adapter.rb:76`. For Rack requests, `RackAdapter#call` builds a request object from the Rack environment at `lib/yard/server/rack_adapter.rb:58` and passes it to `router.call(request)` at `lib/yard/server/rack_adapter.rb:60`. `Router#call` then stores the incoming request at `lib/yard/server/router.rb:55` and invokes `check_static_cache` before normal routing at `lib/yard/server/router.rb:56`. Inside `check_static_cache`, the only initial guard is that `adapter.document_root` is present at `lib/yard/server/static_caching.rb:35`; the cache path is built from `File.join(adapter.document_root, request.path.sub(/\.html$/, '') + '.html')` at `lib/yard/server/static_caching.rb:36`, without cleaning `..` components first. If that resolved path is a regular file, `File.file?` accepts it at `lib/yard/server/static_caching.rb:38` and the file bytes are returned as a `200` HTML response at `lib/yard/server/static_caching.rb:40`. The later route sanitizer in `final_options` uses `File.cleanpath(...).gsub(...)` at `lib/yard/server/router.rb:181` and `lib/yard/server/router.rb:182`, but a static-cache hit returns before that code is reached.

### PoC
[poc.zip](https://github.com/user-attachments/files/28185421/poc.zip)

```bash
bash ./poc/run.sh
```
expected output:
```text
run 1: exit=0 timed_out=False duration=0.08s matched=True phase=oracle fingerprint='YARD_STATIC_CACHE_PATH_TRAVERSAL'
run 2: exit=0 timed_out=False duration=0.08s matched=True phase=oracle fingerprint='YARD_STATIC_CACHE_PATH_TRAVERSAL'
run 3: exit=0 timed_out=False duration=0.08s matched=True phase=oracle fingerprint='YARD_STATIC_CACHE_PATH_TRAVERSAL'
```

The `YARD_STATIC_CACHE_PATH_TRAVERSAL` fingerprint is emitted only after the PoC observes a `200` static-cache response whose body contains the sibling file outside the configured document root. A setup failure, syntax failure, or cache miss would not print this oracle and would not demonstrate this traversal read.

### Impact
A remote unauthenticated HTTP client who can reach a YARD documentation server with `DocumentRoot`/`--docroot` enabled can request `.html` paths containing parent-directory components and receive readable matching files outside the configured document root. The required guards are narrow: `adapter.document_root` must be set, the traversed target must exist as a regular readable file, and the target must be reachable through the implementation's forced `.html` suffix. Those requests bypass the later `final_options` path cleanup because the cache check runs first. The resulting severity class is information disclosure: response bodies can contain off-root `.html` file contents, but this path does not show write access, code execution, or arbitrary files without the `.html` constraint.

## References
- https://github.com/lsegal/yard/security/advisories/GHSA-pxcc-8665-phx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-49342
- https://github.com/lsegal/yard/commit/f78c19f0dd33a407085b4ed181bb60c0aa0078b4
- https://github.com/lsegal/yard
