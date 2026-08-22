# [H] "Assertion failed" in node::http2::Http2Session::~Http2Session() leads to HTTP/2 server crash

## Summary
Severity: High (CVSS 8.2)
Program: Node.js
Weakness: Uncontrolled Resource Consumption
Reporter: bart
State: resolved
Disclosed: 2024-04-08T22:25:42.342Z
CVE: CVE-2024-27983
Source: https://hackerone.com/reports/2319584

## Details
**Summary:**

I discovered a vulnerability in Node.js HTTP/2 stack (`http2`) package. An attacker can send a very small amount of TCP packets with a few HTTP/2 frames inside. After a few seconds a Node.js (latest: 21.5.0 and latest LTS: v20.11.0) server crash with the following stack:
```
  #  node[3253]: virtual node::http2::Http2Session::~Http2Session() at ../src/node_http2.cc:534
  #  Assertion failed: (current_nghttp2_memory_) == (0)

----- Native stack trace -----

 1: 0xca5430 node::Abort() [node]
 2: 0xca54b0 node::errors::SetPrepareStackTraceCallback(v8::FunctionCallbackInfo<v8::Value> const&) [node]
 3: 0xce7156 node::http2::Http2Session::~Http2Session() [node]
 4: 0xce7192 node::http2::Http2Session::~Http2Session() [node]
 5: 0x106f01d v8::internal::GlobalHandles::InvokeFirstPassWeakCallbacks() [node]
 6: 0x10f3215 v8::internal::Heap::PerformGarbageCollection(v8::internal::GarbageCollector, v8::internal::GarbageCollectionReason, char const*) [node]
 7: 0x10f3d7c v8::internal::Heap::CollectGarbage(v8::internal::AllocationSpace, v8::internal::GarbageCollectionReason, v8::GCCallbackFlags) [node]
 8: 0x10ca081 v8::internal::HeapAllocator::AllocateRawWithLightRetrySlowPath(int, v8::internal::AllocationType, v8::internal::AllocationOrigin, v8::internal::AllocationAlignment) [node]
 9: 0x10cb215 v8::internal::HeapAllocator::AllocateRawWithRetryOrFailSlowPath(int, v8::internal::AllocationType, v8::internal::AllocationOrigin, v8::internal::AllocationAlignment) [node]
10: 0x10a8866 v8::internal::Factory::NewFillerObject(int, v8::internal::AllocationAlignment, v8::internal::AllocationType, v8::internal::AllocationOrigin) [node]
11: 0x15035f6 v8::internal::Runtime_AllocateInYoungGeneration(int, unsigned long*, v8::internal::Isolate*) [node]
12: 0x7f41df699ef6 
Aborted (core dumped)
```
The attack is easy to perform so a permanent Denial of Service is possible. It is also hard to debug from server admins (check Impact section).

**Description:**

The `http2` package has an  assertion in the `Http2Session` destructor which check if current memory usage of nghttp2 library (`current_nghttp2_memory_`) has been reset to 0.
```c++
Http2Session::~Http2Session() {
  CHECK(!is_in_scope());
  Debug(this, "freeing nghttp2 session");
  // Explicitly reset session_ so the subsequent
  // current_nghttp2_memory_ check passes.
  session_.reset();
  CHECK_EQ(current_nghttp2_memory_, 0);
}
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2319584_
