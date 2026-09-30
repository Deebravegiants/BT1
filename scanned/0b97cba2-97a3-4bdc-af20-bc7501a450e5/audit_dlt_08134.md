# [?] p2p: fix deadlock banning while updating peer lists

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-12-31
Source: https://github.com/monero-project/monero/commit/656b2f7ce14bfc6125e76eeef480f91a37b10b8a
Type: security-commit

## Details
p2p: fix deadlock banning while updating peer lists

## Patch
### src/p2p/net_node.inl
```diff
@@ -2149,6 +2149,7 @@ namespace nodetool
 
     LOG_DEBUG_CC(context, "REMOTE PEERLIST: remote peerlist size=" << peerlist_.size());
     LOG_TRACE_CC(context, "REMOTE PEERLIST: " << ENDL << print_peerlist_to_string(peerlist_));
+    CRITICAL_REGION_LOCAL(m_blocked_hosts_lock);
     return m_network_zones.at(context.m_remote_address.get_zone()).m_peerlist.merge_peerlist(peerlist_, [this](const peerlist_entry &pe) {
       return !is_addr_recently_failed(pe.adr) && is_remote_host_allowed(pe.adr);
     });
```
