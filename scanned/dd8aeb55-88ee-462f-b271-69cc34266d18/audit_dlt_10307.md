# [?] contracts/chequebook/contract: fix possible reentrancy bug in chequebook.sol

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin-archive
Published: 2016-08-30
Source: https://github.com/axieinfinity/ronin-archive/commit/7b884e0075cba9033dadf2d8ed0bf092193d2ae5
Type: security-commit

## Details
contracts/chequebook/contract: fix possible reentrancy bug in chequebook.sol

## Patch
### build/update-license.go
```diff
@@ -51,6 +51,7 @@ var (
 		"crypto/secp256k1/curve.go",
 		"trie/arc.go",
 		// don't license generated files
+		"contracts/chequebook/contract/",
 		"contracts/ens/contract/",
 	}
 
```

### contracts/chequebook/contract/chequebook.go
```diff
@@ -1,18 +1,5 @@
-// Copyright 2016 The go-ethereum Authors
-// This file is part of the go-ethereum library.
-//
-// The go-ethereum library is free software: you can redistribute it and/or modify
-// it under the terms of the GNU Lesser General Public License as published by
-// the Free Software Foundation, either version 3 of the License, or
-// (at your option) any later version.
-//
-// The go-ethereum library is distributed in the hope that it will be useful,
-// but WITHOUT ANY WARRANTY; without even the implied warranty of
-// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-// GNU Lesser General Public License for more details.
-//
-// You should have received a copy of the GNU Lesser General Public License
-// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
+// This file is an automatically generated Go binding. Do not modify as any
+// change will likely be lost upon the next re-generation!
 
 package contract
 
@@ -30,7 +17,7 @@ import (
 const ChequebookABI = `[{"constant":false,"inputs":[],"name":"kill","outputs":[],"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"sent","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"beneficiary","type":"address"},{"name":"amount","type":"uint256"},{"name":"sig_v","type":"uint8"},{"name":"sig_r","type":"bytes32"},{"name":"sig_s","type":"bytes32"}],"name":"cash","outputs":[],"type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"deadbeat","type":"address"}],"name":"Overdraft","type":"event"}]`
 
 // ChequebookBin is the compiled bytecode used for deploying new contracts.
-const ChequebookBin = `0x606060405260008054600160a060020a03191633179055610223806100246000396000f3606060405260e060020a600035046341c0e1b581146100315780637bf786f814610059578063fbf788d614610071575b005b61002f60005433600160a060020a03908116911614156100b957600054600160a060020a0316ff5b6100a760043560016020526000908152604090205481565b61002f600435602435604435606435608435600160a060020a03851660009081526001602052604081205485116100bb576101cf565b60408051918252519081900360200190f35b565b50604080516c0100000000000000000000000030600160a060020a0390811682028352881602601482015260288101869052815190819003604801812080825260ff861660208381019190915282840186905260608301859052925190926001926080818101939182900301816000866161da5a03f11561000257505060405151600054600160a060020a03908116911614610156576101cf565b600160a060020a038681166000908152600160205260409020543090911631908603106101d75760406000818120549151600160a060020a0389169288039082818181858883f19350505050156101cf57846001600050600088600160a060020a03168152602001908152602001600020600050819055505b505050505050565b60005460408051600160a060020a03929092168252517f2250e2993c15843b32621c89447cc589ee7a9f049c026986e545d3c2c0c6f9789181900360200190a185600160a060020a0316ff`
+const ChequebookBin = `0x606060405260008054600160a060020a031916331790556101ff806100246000396000f3606060405260e060020a600035046341c0e1b581146100315780637bf786f814610059578063fbf788d614610071575b005b61002f60005433600160a060020a03908116911614156100bd57600054600160a060020a0316ff5b6100ab60043560016020526000908152604090205481565b61002f600435602435604435606435608435600160a060020a03851660009081526001602052604081205485116100bf575b505050505050565b60408051918252519081900360200190f35b565b50604080516c0100000000000000000000000030600160a060020a0390811682028352881602601482015260288101869052815190819003604801812080825260ff861660208381019190915282840186905260608301859052925190926001926080818101939182900301816000866161da5a03f11561000257505060405151600054600160a060020a0390811691161461015a576100a3565b600160a060020a038681166000908152600160205260409020543090911631908603106101b357604060008181208790559051600160a060020a0388169190819081818181818881f1935050505015156100a357610002565b60005460408051600160a060020a03929092168252517f2250e2993c15843b32621c89447cc589ee7a9f049c026986e545d3c2c0c6f9789181900360200190a185600160a060020a0316ff`
 
 // DeployChequebook deploys a new Ethereum contract, binding an instance of Chequebook to it.
 func DeployChequebook(auth *bind.TransactOpts, backend bind.ContractBackend) (common.Address, *types.Transaction, *Chequebook, error) {
```

### contracts/chequebook/contract/chequebook.sol
```diff
@@ -28,9 +28,11 @@ contract chequebook is mortal {
         // Attempt sending the difference between the cumulative amount on the cheque
         // and the cumulative amount on the last cashed cheque to beneficiary.
         if (amount - sent[beneficiary] >= this.balance) {
-            if (beneficiary.send(amount - sent[beneficiary])) {
-                // Upon success, update the cumulative amount.
-                sent[beneficiary] = amount;
+	    // update the cumulative amount before sending
+            sent[beneficiary] = amount;
+            if (!beneficiary.send(amount - sent[beneficiary])) {
+                // Upon failure to execute send, revert everything
+                throw;
             }
         } else {
             // Upon failure, punish owner for writing a bounced cheque.
```

### contracts/chequebook/contract/code.go
```diff
@@ -1,21 +1,5 @@
-// Copyright 2016 The go-ethereum Authors
-// This file is part of the go-ethereum library.
-//
-// The go-ethereum library is free software: you can redistribute it and/or modify
-// it under the terms of the GNU Lesser General Public License as published by
-// the Free Software Foundation, either version 3 of the License, or
-// (at your option) any later version.
-//
-// The go-ethereum library is distributed in the hope that it will be useful,
-// but WITHOUT ANY WARRANTY; without even the implied warranty of
-// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-// GNU Lesser General Public License for more details.
-//
-// You should have received a copy of the GNU Lesser General Public License
-// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.
-
 package contract
 
 // ContractDeployedCode is used to detect suicides. This constant needs to be
 // updated when the contract code is changed.
-const ContractDeployedCode = "0x606060405260e060020a600035046341c0e1b581146100315780637bf786f814610059578063fbf788d614610071575b005b61002f60005433600160a060020a03908116911614156100b957600054600160a060020a0316ff5b6100a760043560016020526000908152604090205481565b61002f600435602435604435606435608435600160a060020a03851660009081526001602052604081205485116100bb576101cf565b60408051918252519081900360200190f35b565b50604080516c0100000000000000000000000030600160a060020a0390811682028352881602601482015260288101869052815190819003604801812080825260ff861660208381019190915282840186905260608301859052925190926001926080818101939182900301816000866161da5a03f11561000257505060405151600054600160a060020a03908116911614610156576101cf565b600160a060020a038681166000908152600160205260409020543090911631908603106101d75760406000818120549151600160a060020a0389169288039082818181858883f19350505050156101cf57846001600050600088600160a060020a03168152602001908152602001600020600050819055505b505050505050565b60005460408051600160a060020a03929092168252517f2250e2993c15843b32621c89447cc589ee7a9f049c026986e545d3c2c0c6f9789181900360200190a185600160a060020a0316ff"
+const ContractDeployedCode = "0x606060405260e060020a600035046341c0e1b581146100315780637bf786f814610059578063fbf788d614610071575b005b61002f60005433600160a060020a03908116911614156100bd57600054600160a060020a0316ff5b6100ab60043560016020526000908152604090205481565b61002f600435602435604435606435608435600160a060020a03851660009081526001602052604081205485116100bf575b505050505050565b60408051918252519081900360200190f35b565b50604080516c0100000000000000000000000030600160a060020a0390811682028352881602601482015260288101869052815190819003604801812080825260ff861660208381019190915282840186905260608301859052925190926001926080818101939182900301816000866161da5a03f11561000257505060405151600054600160a060020a0390811691161461015a576100a3565b600160a060020a038681166000908152600160205260409020543090911631908603106101b357604060008181208790559051600160a060020a0388169190819081818181818881f1935050505015156100a357610002565b60005460408051600160a060020a03929092168252517f2250e2993c15843b32621c89447cc589ee7a9f049c026986e545d3c2c0c6f9789181900360200190a185600160a060020a0316ff"
```

### contracts/chequebook/gencode.go
```diff
@@ -59,9 +59,7 @@ func main() {
 	}
 
 	// Write the output file.
-	content := fmt.Sprintf(`// TODO: insert license header
-
-package contract
+	content := fmt.Sprintf(`package contract
 
 // ContractDeployedCode is used to detect suicides. This constant needs to be
 // updated when the contract code is changed.
```
