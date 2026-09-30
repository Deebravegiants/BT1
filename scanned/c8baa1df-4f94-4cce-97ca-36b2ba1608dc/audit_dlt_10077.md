# [?] Fix a crash that would sometimes happen in debug builds at handshakes (#3459)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-09-20
Source: https://github.com/nanocurrency/nano-node/commit/5c66c28dab693c37880264bdad8c3ac14c78213e
Type: security-commit

## Details
Fix a crash that would sometimes happen in debug builds at handshakes (#3459)

## Patch
### nano/node/transport/tcp.cpp
```diff
@@ -538,7 +538,7 @@ void nano::transport::tcp_channels::start_tcp (nano::endpoint const & endpoint_a
 				nano::node_id_handshake message (node_l->network_params.network, cookie, boost::none);
 				if (node_l->config.logging.network_node_id_handshake_logging ())
 				{
-					node_l->logger.try_log (boost::str (boost::format ("Node ID handshake request sent with node ID %1% to %2%: query %3%") % node_l->node_id.pub.to_node_id () % endpoint_a % (*cookie).to_string ()));
+					node_l->logger.try_log (boost::str (boost::format ("Node ID handshake request sent with node ID %1% to %2%: query %3%") % node_l->node_id.pub.to_node_id () % endpoint_a % (cookie.has_value() ? cookie->to_string() : "not set")));
 				}
 				channel->set_endpoint ();
 				std::shared_ptr<std::vector<uint8_t>> receive_buffer (std::make_shared<std::vector<uint8_t>> ());
```
