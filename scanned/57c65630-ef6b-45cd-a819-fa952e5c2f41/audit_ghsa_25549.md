# [H] Relative Path Traversal in afire serve_static

## Summary
Severity: High
Advisory: GHSA-3227-r97m-8j95
CWE: CWE-22, CWE-34
Ecosystem: crates.io
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-3227-r97m-8j95
Type: github-advisory

## Affected
- crates.io: `afire` — affected >=0.2.1 <1.1.0

## Details
### Impact
This vulnerability effects the built-in afire serve_static extension allowing paths containing `//....` to bypass the previous path sanitation and request files in higher directories that should not be accessible.

### Patches
The issue has been fixed in [afire 1.1.0](https://crates.io/crates/afire/1.1.0).
If you can, just update to the newest version of afire.

### Workarounds
If you can't update afire you can simply disallow paths containing `/..` with the following middleware.
Make sure this is the last middleware added to the server so it runs first, stopping the bad requests.
```rust
use afire::prelude::*;

struct PathTraversalFix;

impl Middleware for PathTraversalFix {
    fn pre(&self, req: Request) -> MiddleRequest {
        if req.path.replace("\\", "/").contains("/..") {
            return MiddleRequest::Send(
                Response::new()
                    .status(400)
                    .text("Paths containing `..` are not allowed"),
            );
        }

        MiddleRequest::Continue
    }
}
```
```rust
let mut server = Server::new(host, port);
PathTraversalFix.attach(&mut server);
```

### References
You can read about the new changes to afire in 1.1.0 [here](https://connorcode.com/writing/afire/update-3)

### For more information
If you have any questions or comments about this advisory you can email me or message me on discord.
[[https://connorcode.com/contact](https://connorcode.com/contact)]

## References
- https://github.com/Basicprogrammer10/afire/security/advisories/GHSA-3227-r97m-8j95
- https://github.com/Basicprogrammer10/afire/commit/da7904c04f82e1cb43cc42eaf6a1dba072b5c921
- https://github.com/Basicprogrammer10/afire
- https://github.com/Basicprogrammer10/afire/releases/tag/v1.1.0
