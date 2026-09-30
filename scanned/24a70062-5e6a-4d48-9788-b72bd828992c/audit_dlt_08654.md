# [?] Fix tonlib client crashing when block lookup error (#979)

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2024-07-17
Source: https://github.com/ton-blockchain/ton/commit/015e2e55d3df550fe89899dd50f7fb1845125def
Type: security-commit

## Details
Fix tonlib client crashing when block lookup error (#979)

Co-authored-by: hey-researcher <ton-researcher@pm.me>

## Patch
### tonlib/tonlib/TonlibClient.cpp
```diff
@@ -5574,6 +5574,11 @@ td::Status TonlibClient::do_request(const tonlib_api::blocks_lookupBlock& reques
   client_.with_last_block(
     [self = this, blkid, lite_block = std::move(lite_block), mode = request.mode_, lt = (td::uint64)request.lt_, 
     utime = (td::uint32)request.utime_, promise = std::move(promise)](td::Result<LastBlockState> r_last_block) mutable { 
+      if (r_last_block.is_error()) {
+        promise.set_error(r_last_block.move_as_error_prefix(TonlibError::Internal("get last block failed ")));
+        return;
+      }
+
       self->client_.send_query(ton::lite_api::liteServer_lookupBlockWithProof(mode, std::move(lite_block), ton::create_tl_lite_block_id(r_last_block.ok().last_block_id), lt, utime),
         promise.wrap([blkid, mode, utime, lt, last_block = r_last_block.ok().last_block_id](lite_api_ptr<ton::lite_api::liteServer_lookupBlockResult>&& result) 
                                           -> td::Result<object_ptr<tonlib_api::ton_blockIdExt>> {
```
