# [?] Caplin: fixed `node/identity` crashes (#14194)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-18
Source: https://github.com/erigontech/erigon/commit/a92942331fbd8f079e974c9ec95e0977a2d9c18a
Type: security-commit

## Details
Caplin: fixed `node/identity` crashes (#14194)

## Patch
### cl/sentinel/sentinel.go
```diff
@@ -30,6 +30,7 @@ import (
 
 	"github.com/c2h5oh/datasize"
 	"github.com/go-chi/chi/v5"
+	"github.com/prysmaticlabs/go-bitfield"
 
 	"github.com/libp2p/go-libp2p"
 	pubsub "github.com/libp2p/go-libp2p-pubsub"
@@ -550,20 +551,20 @@ func (s *Sentinel) Identity() (pid, enrStr string, p2pAddresses, discoveryAddres
 		port := s.listener.LocalNode().Node().UDP()
 		discoveryAddresses = append(discoveryAddresses, fmt.Sprintf("/%s/%s/udp/%d/p2p/%s", protocol, s.listener.LocalNode().Node().IP(), port, pid))
 	}
-	subnetField := [8]byte{}
-	syncnetField := [1]byte{}
-	attSubEnr := enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, subnetField[:])
-	syncNetEnr := enr.WithEntry(s.cfg.NetworkConfig.SyncCommsSubnetKey, syncnetField[:])
+	subnetField := bitfield.NewBitvector64()
+	syncnetField := bitfield.NewBitvector8()
+	attSubEnr := enr.WithEntry(s.cfg.NetworkConfig.AttSubnetKey, &subnetField)
+	syncNetEnr := enr.WithEntry(s.cfg.NetworkConfig.SyncCommsSubnetKey, &syncnetField)
 	if err := s.listener.LocalNode().Node().Load(attSubEnr); err != nil {
-		return
+		s.logger.Debug("[IDENTITY] Could not load att subnet", "err", err)
 	}
 	if err := s.listener.LocalNode().Node().Load(syncNetEnr); err != nil {
-		return
+		s.logger.Debug("[IDENTITY] Could not load sync subnet", "err", err)
 	}
 	metadata = &cltypes.Metadata{
 		SeqNumber: s.listener.LocalNode().Seq(),
-		Attnets:   subnetField,
-		Syncnets:  &syncnetField,
+		Attnets:   [8]byte(subnetField),
+		Syncnets:  (*[1]byte)(syncnetField),
 	}
 	return
 }
```
