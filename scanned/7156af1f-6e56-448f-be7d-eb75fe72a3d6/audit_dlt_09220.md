# [?] fix ipfs swarm peering crash in offline mode (#9261)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2022-10-13
Source: https://github.com/ipfs/kubo/commit/b5fe82496458beb294cd6d612c015a2accf26c2b
Type: security-commit

## Details
fix ipfs swarm peering crash in offline mode (#9261)

## Patch
### core/commands/swarm.go
```diff
@@ -123,6 +123,9 @@ var swarmPeeringAddCmd = &cmds.Command{
 		if err != nil {
 			return err
 		}
+		if !node.IsOnline {
+			return ErrNotOnline
+		}
 
 		for _, addrinfo := range addInfos {
 			node.Peering.AddPeer(addrinfo)
@@ -154,6 +157,10 @@ var swarmPeeringLsCmd = &cmds.Command{
 		if err != nil {
 			return err
 		}
+		if !node.IsOnline {
+			return ErrNotOnline
+		}
+
 		peers := node.Peering.ListPeers()
 		return cmds.EmitOnce(res, addrInfos{Peers: peers})
 	},
@@ -190,6 +197,9 @@ var swarmPeeringRmCmd = &cmds.Command{
 		if err != nil {
 			return err
 		}
+		if !node.IsOnline {
+			return ErrNotOnline
+		}
 
 		for _, arg := range req.Arguments {
 			id, err := peer.Decode(arg)
@@ -207,7 +217,7 @@ var swarmPeeringRmCmd = &cmds.Command{
 	Type: peeringResult{},
 	Encoders: cmds.EncoderMap{
 		cmds.Text: cmds.MakeTypedEncoder(func(req *cmds.Request, w io.Writer, pr *peeringResult) error {
-			fmt.Fprintf(w, "add %s %s\n", pr.ID.String(), pr.Status)
+			fmt.Fprintf(w, "remove %s %s\n", pr.ID.String(), pr.Status)
 			return nil
 		}),
 	},
@@ -853,7 +863,7 @@ Filters default to those specified under the "Swarm.AddrFilters" config key.
 			return err
 		}
 
-		if n.PeerHost == nil {
+		if !n.IsOnline {
 			return ErrNotOnline
 		}
 
@@ -889,7 +899,7 @@ var swarmFiltersAddCmd = &cmds.Command{
 			return err
 		}
 
-		if n.PeerHost == nil {
+		if !n.IsOnline {
 			return ErrNotOnline
 		}
 
@@ -945,7 +955,7 @@ var swarmFiltersRmCmd = &cmds.Command{
 			return err
 		}
 
-		if n.PeerHost == nil {
+		if !n.IsOnline {
 			return ErrNotOnline
 		}
 
```
