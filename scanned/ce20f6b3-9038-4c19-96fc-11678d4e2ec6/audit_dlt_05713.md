# [?] lightningd: fix log crash on weird escape lines from plugin.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-06-10
Source: https://github.com/ElementsProject/lightning/commit/03b4f4778e8c9119fed30b9ad098851dfd9145a2
Type: security-commit

## Details
lightningd: fix log crash on weird escape lines from plugin.

Apparently clboss gives us \u UTF codes.  We don't support that (use UTF-8 directly)

```
126	../sysdeps/x86_64/multiarch/strlen-vec.S: No such file or directory.
(gdb) bt
    label=label@entry=0x63e2f9604db9 "char *[]") at ccan/ccan/tal/str/str.c:137
    complete=complete@entry=0x7ffe9090b0f6, destroyed=destroyed@entry=0x7ffe9090b0f7) at lightningd/plugin.c:773
```

Reported-by: Ken Sedgwick
Fixes: #8338
Changelog-None: broken in this release
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
