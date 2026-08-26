# [H] `set_daemon` wallet-rpc silently ignores `ssl_allowed_fingerprints` → pinning bypassed, wallet↔daemon MITM

## Summary
Severity: High (CVSS 7.7)
Program: Monero
Weakness: Improper Certificate Validation
Reporter: benisprlh
State: resolved
Disclosed: 2026-08-05T05:05:59.944Z
Source: https://hackerone.com/reports/3686259

## Details
**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet_rpc_server.cpp` (shared vulnerable code also reached via `contrib/epee/src/net_ssl.cpp`). Affected branches: `master` (commit `230de3794`), `release-v0.18`, `release-v0.17` (and every release since the RPC was introduced in commit `67aa4adcf`, March 2019).

## Summary

The `set_daemon` JSON-RPC in `monero-wallet-rpc` accepts an `ssl_allowed_fingerprints` array and is supposed to pin the daemon's TLS cert to the listed SHA-256 digests. The handler never hex-decodes those strings — it just copies each character into the fingerprint buffer as a byte. A normal 64-char hex fingerprint ends up stored as 64 bytes of ASCII instead of 32 bytes of raw digest. `has_fingerprint()` later compares the real 32-byte SHA-256 of the peer cert against those 64-byte blobs with `std::binary_search`, so the check can never succeed. Because the command's default `ssl_support` is `"autodetect"`, the verify callback turns "nothing matched" into a `MWARNING` and accepts the connection anyway. Pinning is silently discarded.

The sibling CLI flag `--daemon-ssl-allowed-fingerprints` on the exact same binary goes through `epee::from_hex_locale::to_vector` and enforces `SSL_FINGERPRINT_SIZE == 32`. So the two paths accept the same documented input format and produce opposite security outcomes.

Buggy block, `src/wallet/wallet_rpc_server.cpp` (current master `230de3794`):

```cpp
std::vector<std::vector<uint8_t>> ssl_allowed_fingerprints;
ssl_allowed_fingerprints.reserve(req.ssl_allowed_fingerprints.size());
for (const std::string &fp: req.ssl_allowed_fingerprints)
{
  ssl_allowed_fingerprints.push_back({});
  std::vector<uint8_t> &v = ssl_allowed_fingerprints.back();
  for (auto c: fp)
    v.push_back(c);
}
```

Correct block, `src/wallet/wallet2.cpp` (CLI startup):

```cpp
std::vector<std::vector<uint8_t>> ssl_allowed_fingerprints{ daemon_ssl_allowed_fingerprints.size() };
std::transform(daemon_ssl_allowed_fingerprints.begin(), daemon_ssl_allowed_fingerprints.end(),
               ssl_allowed_fingerprints.begin(), epee::from_hex_locale::to_vector);
for (const auto &fpr: ssl_allowed_fingerprints)
{
  THROW_WALLET_EXCEPTION_IF(fpr.size() != SSL_FINGERPRINT_SIZE, tools::error::wallet_internal_error,
      "SHA-256 fingerprint should be " BOOST_PP_STRINGIZE(SSL_FINGERPRINT_SIZE) " bytes long.");
}
```

The decisive check in `contrib/epee/src/net_ssl.cpp`:

```cpp
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3686259_
