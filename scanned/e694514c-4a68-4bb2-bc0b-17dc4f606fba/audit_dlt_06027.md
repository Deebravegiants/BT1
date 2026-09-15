# [?] fix(docs): Fix Docusaurus build crash    (#12365)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-07-22
Source: https://github.com/iotaledger/iota/commit/07338dd7ad47e0c4959415e2027af4133a2cb0a7
Type: security-commit

## Details
fix(docs): Fix Docusaurus build crash    (#12365)

# Description of change

## Problem
The Docusaurus build crashes during compilation of the reference
documentation page for the `package_metadata` framework module.
The `try_get_modules_metadata_v1` function contains two dereference
operators, where each `*` appears immediately after a `(`.

During the docs build, docgen renders the identifiers as links with the
`<Link>` tag, so the `(*` triggering sequence becomes `(*<`. This
sequence is parsed as MDX and it acts as both an opening and a closing
emphasis delimiter, so the two `*` pair up: the text between them is
rendered into an `<em>` whose first child is a `<Link>` element.

The build's `rehype-jargon` plugin assumes every `<em>`'s first child is
plain text and calls `.toLowerCase()` on it. A `<Link>` element has no
text value, so the call throws and aborts the whole build.

## Fix

- (Root cause): Escape `*` in the framework docgen so it can never be
read as markdown emphasis.
- (Workaround): Make docusaurus aware of this pattern and add an empty
text value inside the `<em>` block, so it won't fail during the build
process

## Changes

- `crates/iota-framework/tests/build-system-packages.rs`: escape `*`
alongside `{` when emitting code blocks in `relocate_docs`.
- `docs/site/config/rehype-jargon-safe.js` (new): wrap rehype-jargon so
an `<em>` whose first child is not a text node can't crash the build.
- `docs/site/docusaurus.config.js`: use the safe wrapper.

## **Why both fixes are needed now**

**Framework reference docs are not generated per-PR: the Docusaurus
build downloads them from a prebuilt S3 archive, which is only
regenerated and republished on pushes to `devnet/testnet/mainnet`. The
current devnet archive contains the unescaped .`mdx` that triggers the
crash.**
**The parser fix only changes what the generator produces and it does
not touch the S3 archive. Until a new release recompiles and republishes
it, every PR that touches docs downloads the same broken archive and
hits the same crash, regardless of the PR's content.**
**The parser fix therefore does not unblock CI on its own right now. The
Docusaurus guard is what unblocks it, and it works independently of the
archive. The guard must be used until the recompiled archive is
released. It can be removed once the escaped docs are live on S3.**

**The workaround only makes the docs build, but it doesn't undo the
emphasis. So for now the `*` are not shown in `PackageMetadata`
reference until we ship a new release.**

## Links to any relevant issues

fixes #12355

## How the change has been tested

Locally reproduced and tested.

### crates/iota-framework/tests/build-system-packages.rs
```diff
@@ -301,7 +301,9 @@ fn relocate_docs(files: &[(String, String)], output: &mut BTreeMap<String, Strin
         // from mdx. MDX also strips leading whitespace inside `<code>` blocks
         // (it parses the content as a paragraph), which silently drops indentation
         // from Move implementations — encode leading spaces as `&nbsp;` so the
-        // browser still renders them as regular spaces.
+        // browser still renders them as regular spaces. Escape `*` as well: MDX
+        // parses the block content as markdown, so a pair of `*` (e.g. two `*x`
+        // dereferences) would be read as emphasis and mangle the code.
         let content = code_regex.replace_all(&content, |caps: &regex::Captures| {
             let match_content = caps.get(0).unwrap().as_str();
             let code_content = caps.get(1).unwrap().as_str();
@@ -310,6 +312,7 @@ fn relocate_docs(files: &[(String, String)], output: &mut BTreeMap<String, Strin
             }
             let escaped = code_content
                 .replace('{', "\\{")
+                .replace('*', "\\*")
                 .split('\n')
                 .map(|line| {
                     let stripped = line.trim_start_matches(' ');
```

### docs/site/config/rehype-jargon-safe.js
```diff
@@ -0,0 +1,35 @@
+// Copyright (c) 2026 IOTA Stiftung
+// SPDX-License-Identifier: Apache-2.0
+
+const jargonModule = require("rehype-jargon");
+
+// rehype-jargon@3.1.0 assumes every <em> node's first child is a text node and
+// calls `children[0].value.toLowerCase()` on it. Generated Move reference docs
+// can produce an <em> that wraps a JSX element instead of text — for example a
+// `(*x)` dereference that CommonMark reads as emphasis — whose first child has
+// no `value`, which throws and aborts the whole build. Prepending an empty text
+// node makes the term lookup miss safely instead of crashing.
+function guardEmphasisFirstChild(node) {
+  if (!node || typeof node !== "object") return;
+
+  if (node.tagName === "em") {
+    const first = node.children && node.children[0];
+    if (!first || typeof first.value !== "string") {
+      node.children = node.children || [];
+      node.children.unshift({ type: "text", value: "" });
+    }
+  }
+
+  if (Array.isArray(node.children)) {
+    for (const child of node.children) guardEmphasisFirstChild(child);
+  }
+}
+
+module.exports = function rehypeJargonSafe(options) {
+  const rehypeJargon = jargonModule.default || jargonModule;
+  const transform = rehypeJargon(options);
+  return (tree, file) => {
+    guardEmphasisFirstChild(tree);
+    return transform(tree, file);
+  };
+};
```

### docs/site/docusaurus.config.js
```diff
@@ -437,7 +437,7 @@ const config = {
           ],
           rehypePlugins: [
             katex,
-            [require('rehype-jargon'), { jargon: jargonConfig}]
+            [require('./config/rehype-jargon-safe.js'), { jargon: jargonConfig}]
           ],
         },
         theme: {
```
