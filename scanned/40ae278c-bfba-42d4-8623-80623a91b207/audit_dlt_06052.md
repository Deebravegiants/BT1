# [?] Merge #20479: Fix QPainter non-determinism on macOS (0.21 backport)

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-11-25
Source: https://github.com/litecoin-project/litecoin/commit/17294c1820396791f436e659432c5d0a976c6554
Type: security-commit

## Details
Merge #20479: Fix QPainter non-determinism on macOS (0.21 backport)

ab23a83400d5ad13137ce0f9697a51f0b70e9d29 Fix QPainter non-determinism on macOS (Andrew Chow)

Pull request description:

  Aplies a patch to Qt that fixes the non-determinism by modifying Qt. The
  source of the non-determinism is how LLVM 8 optimizes qt_intersect_spans
  when compiling. The particular optimization that seems to be causing the
  problems is that a temp variable is being added for spans->y. For some
  reason, when it does this, it chooses different instructions to use when
  making that variable. We bypass this problem by patching
  qt_intersect_spans to always make and use this local variable.

  Github-Pull: #20447
  Rebased-From: 8f7d1b39efbe65ab2747c593cc3560d4a449a333
  Tree-SHA512: 558da5c2bb0373e2a89f2c219170f802036e0e87cc8e808336b23d074152cb893007a440f46ec957156b0921355cd18502710f2d224f27bc26e934c50ebebc41

ACKs for top commit:
  jonasschnelli:
    codereview ACK ab23a83400d5ad13137ce0f9697a51f0b70e9d29
  achow101:
    ACK ab23a83400d5ad13137ce0f9697a51f0b70e9d29

Tree-SHA512: 10991fe2b5452b1393678c315281cfdca011e9bb2cd8094a002746e690890ace148ac2dbf39c5fbe5e7f4cd39eeebfa0a715c065cff150cf70e9733cb0ff32d6
