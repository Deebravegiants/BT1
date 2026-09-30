# [?] quic: fix flow control window exhaustion causing hang

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-01-08
Source: https://github.com/ton-blockchain/ton/commit/13f2d85843cf50a3a645f43c800e94aecfcc07c2
Type: security-commit

## Details
quic: fix flow control window exhaustion causing hang

## Patch
### quic/quic-pimpl.cpp
```diff
@@ -584,7 +584,7 @@ int QuicConnectionPImpl::handshake_completed_cb(ngtcp2_conn* conn, void* user_da
   return 0;
 }
 
-int QuicConnectionPImpl::recv_stream_data_cb(ngtcp2_conn*, uint32_t flags, int64_t stream_id, uint64_t offset,
+int QuicConnectionPImpl::recv_stream_data_cb(ngtcp2_conn* conn, uint32_t flags, int64_t stream_id, uint64_t offset,
                                              const uint8_t* data, size_t datalen, void* user_data,
                                              void* stream_user_data) {
   data = data ? data : static_cast<uint8_t*>(user_data);  // stupid hack to create empty slice
@@ -593,6 +593,10 @@ int QuicConnectionPImpl::recv_stream_data_cb(ngtcp2_conn*, uint32_t flags, int64
       .sid = stream_id, .data = td::BufferSlice{data_slice}, .fin = (flags & NGTCP2_STREAM_DATA_FLAG_FIN) != 0};
   auto* pimpl = static_cast<QuicConnectionPImpl*>(user_data);
   pimpl->callback->on_stream_data(std::move(event));
+
+  ngtcp2_conn_extend_max_stream_offset(conn, stream_id, datalen);
+  ngtcp2_conn_extend_max_offset(conn, datalen);
+
   return 0;
 }
 
```
