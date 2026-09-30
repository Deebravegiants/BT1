# [?] fix: panic on using WaitGroup after it is freed (#1464)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2023-04-16
Source: https://github.com/bnb-chain/bsc/commit/2b0f56898d233cefee3b17e8ad61529660f5cd92
Type: security-commit

## Details
fix: panic on using WaitGroup after it is freed (#1464)

## Patch
### core/blockchain.go
```diff
@@ -1584,18 +1584,20 @@ func (bc *BlockChain) writeBlockWithState(block *types.Block, receipts []*types.
 					}
 				}
 				// Garbage collect anything below our required write retention
+				wg2 := sync.WaitGroup{}
 				for !bc.triegc.Empty() {
 					root, number := bc.triegc.Pop()
 					if uint64(-number) > chosen {
 						bc.triegc.Push(root, number)
 						break
 					}
-					wg.Add(1)
+					wg2.Add(1)
 					go func() {
 						triedb.Dereference(root.(common.Hash))
-						wg.Done()
+						wg2.Done()
 					}()
 				}
+				wg2.Wait()
 			}
 		}
 		return nil
```
