# [?] p2p: fix race condition accessing a deleted context

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-12-04
Source: https://github.com/monero-project/monero/commit/281b42a281f275b5cc4a5c49336a94cedd0e3ae5
Type: security-commit

## Details
p2p: fix race condition accessing a deleted context

## Patch
### src/p2p/net_node.h
```diff
@@ -287,7 +287,7 @@ namespace nodetool
     uint32_t get_max_out_public_peers() const;
     void change_max_in_public_peers(size_t count);
     uint32_t get_max_in_public_peers() const;
-    virtual bool block_host(const epee::net_utils::network_address &adress, time_t seconds = P2P_IP_BLOCKTIME);
+    virtual bool block_host(epee::net_utils::network_address address, time_t seconds = P2P_IP_BLOCKTIME);
     virtual bool unblock_host(const epee::net_utils::network_address &address);
     virtual bool block_subnet(const epee::net_utils::ipv4_network_subnet &subnet, time_t seconds = P2P_IP_BLOCKTIME);
     virtual bool unblock_subnet(const epee::net_utils::ipv4_network_subnet &subnet);
```

### src/p2p/net_node.inl
```diff
@@ -224,7 +224,7 @@ namespace nodetool
   }
   //-----------------------------------------------------------------------------------
   template<class t_payload_net_handler>
-  bool node_server<t_payload_net_handler>::block_host(const epee::net_utils::network_address &addr, time_t seconds)
+  bool node_server<t_payload_net_handler>::block_host(epee::net_utils::network_address addr, time_t seconds)
   {
     if(!addr.is_blockable())
       return false;
@@ -237,7 +237,8 @@ namespace nodetool
       limit = std::numeric_limits<time_t>::max();
     else
       limit = now + seconds;
-    m_blocked_hosts[addr.host_str()] = limit;
+    const std::string host_str = addr.host_str();
+    m_blocked_hosts[host_str] = limit;
 
     // drop any connection to that address. This should only have to look into
     // the zone related to the connection, but really make sure everything is
@@ -253,17 +254,18 @@ namespace nodetool
         }
         return true;
       });
-      for (const auto &c: conns)
-        zone.second.m_net_server.get_config_object().close(c);
-
-      conns.clear();
 
       peerlist_entry pe{};
       pe.adr = addr;
       zone.second.m_peerlist.remove_from_peer_white(pe);
+
+      for (const auto &c: conns)
+        zone.second.m_net_server.get_config_object().close(c);
+
+      conns.clear();
     }
 
-    MCLOG_CYAN(el::Level::Info, "global", "Host " << addr.host_str() << " blocked.");
+    MCLOG_CYAN(el::Level::Info, "global", "Host " << host_str << " blocked.");
     return true;
   }
   //-----------------------------------------------------------------------------------
```

### src/p2p/net_node_common.h
```diff
@@ -58,7 +58,7 @@ namespace nodetool
     virtual uint64_t get_public_connections_count()=0;
     virtual void for_each_connection(std::function<bool(t_connection_context&, peerid_type, uint32_t)> f)=0;
     virtual bool for_connection(const boost::uuids::uuid&, std::function<bool(t_connection_context&, peerid_type, uint32_t)> f)=0;
-    virtual bool block_host(const epee::net_utils::network_address &address, time_t seconds = 0)=0;
+    virtual bool block_host(epee::net_utils::network_address address, time_t seconds = 0)=0;
     virtual bool unblock_host(const epee::net_utils::network_address &address)=0;
     virtual std::map<std::string, time_t> get_blocked_hosts()=0;
     virtual std::map<epee::net_utils::ipv4_network_subnet, time_t> get_blocked_subnets()=0;
@@ -108,7 +108,7 @@ namespace nodetool
     {
       return false;
     }
-    virtual bool block_host(const epee::net_utils::network_address &address, time_t seconds)
+    virtual bool block_host(epee::net_utils::network_address address, time_t seconds)
     {
       return true;
     }
```
