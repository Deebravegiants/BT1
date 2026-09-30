# [?] fix panic on nil db (#379)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2018-12-19
Source: https://github.com/iotexproject/iotex-core/commit/511e30bb3cc7b91f0568ba4f99231b1ce7ca8349
Type: security-commit

## Details
fix panic on nil db (#379)

* fix panic on nil db

## Patch
### server/itx/server.go
```diff
@@ -179,7 +179,6 @@ func (s *Server) newSubChainService(cfg config.Config) error {
 	executionProtocol := execution.NewProtocol(cs.Blockchain())
 	cs.AddProtocols(subChainProtocol, accountProtocol, voteProtocol, executionProtocol)
 	s.chainservices[cs.ChainID()] = cs
-	s.dispatcher.AddSubscriber(cs.ChainID(), cs)
 	return nil
 }
 
@@ -211,7 +210,6 @@ func (s *Server) NewTestingChainService(cfg config.Config) error {
 	executionProtocol := execution.NewProtocol(cs.Blockchain())
 	cs.AddProtocols(subChainProtocol, accountProtocol, voteProtocol, executionProtocol)
 	s.chainservices[cs.ChainID()] = cs
-	s.dispatcher.AddSubscriber(cs.ChainID(), cs)
 	return nil
 }
 
```

### server/itx/subchain.go
```diff
@@ -78,6 +78,8 @@ func (s *Server) HandleBlock(blk *blockchain.Block) error {
 					Msg("error when starting the sub-chain")
 				continue
 			}
+			// TODO we may also need to unsubscribing this before stop subcahin
+			s.dispatcher.AddSubscriber(cs.ChainID(), cs)
 			logger.Info().Uint32("sub-chain", subChain.ChainID).Msg("started the sub-chain")
 		}
 	}
```
