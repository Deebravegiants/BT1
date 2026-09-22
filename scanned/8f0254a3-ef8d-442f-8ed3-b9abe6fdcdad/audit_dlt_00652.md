# [?] Merge bitcoin-core/gui#944: Fix out-of-bounds read in RPCParseCommandLine on empty command

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-08-20
Source: https://github.com/bitcoin/bitcoin/commit/87b8a4ee506e3328decbfb304344774797b104f6
Type: security-commit

## Details
Merge bitcoin-core/gui#944: Fix out-of-bounds read in RPCParseCommandLine on empty command

fef99e6563ae284811904b980069166621c4fa22 qt: fix out-of-bounds read in RPCParseCommandLine on empty command (sayed nabhan)

Pull request description:

  When a console line has no command name (it starts with `)`, or is `()`, `(`, or `,`), RPCParseCommandLine reaches the command-execution branch while the current argument frame is still empty, so `stack.back()[0]` reads out of bounds and the argument list built from `stack.back().begin() + 1` to `end()` is an invalid iterator range (throws std::length_error in practice, UBSan flags the null-pointer reference otherwise).

  The `(` branch already guards the frame with `stack.back().size() > 0`, so I add the same check to the `)`/newline branch and the empty frame is skipped. To be clear, `(` alone isn't safe on master either: it fails via the `\n` branch, not via the `(` branch itself (the state there isn't `STATE_ARGUMENT`), and `,` alone fails the same way.

  Since there's no command to run in any of these cases, the parser now returns `false` so the console reports an invalid command line, consistent with other fully-invalid input like a bare `'` or `"`, rather than silently ignoring it.

  Regression cases added to rpcNestedTests for `)`, `()`, `(` and `,` (all abort on master without the guard), plus `getblockchaininfo)` which stays tolerated.

ACKs for top commit:
  hebasto:
    ACK fef99e6563ae284811904b980069166621c4fa22, tested on Ubuntu 26.04.

Tree-SHA512: 15822a0525402878483d5b2d0fe7b9e27916e514c1a8ad4a697f11b1e5cfe33f5fcd1f089efefb976bcf0d84cdf5166a58a070593924c2d4c2e1f8224d06590f
