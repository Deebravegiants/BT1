# [?] Merge bitcoin/bitcoin#34028: p2p: Prevent integer overflow in LocalServiceInfo::nScore

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-06-10
Source: https://github.com/bitcoin/bitcoin/commit/53b836cdcedca79b7504c95b1ba9b6ce7c608b02
Type: security-commit

## Details
Merge bitcoin/bitcoin#34028: p2p: Prevent integer overflow in LocalServiceInfo::nScore

2189a6f5f226d5a2905f1939eb7eea9571502b90 p2p: Saturate LocalServiceInfo::nScore updates at INT_MAX (codeabysss)

Pull request description:

  The overflow for signed arithmetic yields undefined behavior.
  This changes prevents undefined behavior in local address scoring by saturating `nScore` updates at `INT_MAX` in both `SeenLocal()` and `AddLocal()` update paths.

  Fixes: #24049.

ACKs for top commit:
  Crypt-iQ:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90 pending CI
  achow101:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90
  sedited:
    ACK 2189a6f5f226d5a2905f1939eb7eea9571502b90

Tree-SHA512: b861e58ec9d6e18b17768f5cbee31ee825717e1a7216c332eb6fcbe63a7ac24e213ba638aea6f03cb710d9c2d8fe736cc626f11011ed66c3938acf6c38b0ef2a
