# [?] avoid possible null dereference when logging

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2022-04-01
Source: https://github.com/stellar/stellar-core/commit/8e956b6dc9d94acf86221f3799660ad6365d6644
Type: security-commit

## Details
avoid possible null dereference when logging

## Patch
### src/overlay/OverlayManagerImpl.cpp
```diff
@@ -324,7 +324,7 @@ OverlayManagerImpl::connectToImpl(PeerBareAddress const& address,
             CLOG_DEBUG(Overlay,
                        "Peer rejected - all outbound pending connections "
                        "taken: {}",
-                       currentConnection->toString());
+                       address.toString());
             return false;
         }
         getPeerManager().update(address, PeerManager::BackOffUpdate::INCREASE);
```
