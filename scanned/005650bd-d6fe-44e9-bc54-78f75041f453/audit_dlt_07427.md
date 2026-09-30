# [?] Double Spend Proof (dsproof-beta) functional test + test framework adaptations

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-01-25
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/54466c7e195b63dd5b869feb47abee6a55bbae63
Type: security-commit

## Details
Double Spend Proof (dsproof-beta) functional test + test framework adaptations

Co-authored-by: Calin Culianu <calin.culianu@gmail.com>
Co-authored-by: freetrader <freetrader@tuta.io>

Adds the new functional test `bchn-feature-doublespend-proof.py`.

In the test framework, support for the new INV type and `dsproof-beta` network
message is added, along with classes CDSProof and CDSProofSpender which
facilitate serialization/deserialization of double spend proofs

Test plan:
- cmake: `ninja all check-functional-extended`
- autoconf: `make && test/functional/test_runner.py --extended`

## Patch
### test/functional/bchn-feature-doublespend-proof.py
```diff
@@ -0,0 +1,317 @@
+#!/usr/bin/env python3
+# Copyright (c) 2020-2021 The Bitcoin Cash Node developers
+# Distributed under the MIT software license, see the accompanying
+# file COPYING or http://www.opensource.org/licenses/mit-license.php.
+""" Test for the DoubleSpend Proof facility """
+
+import os
+from decimal import Decimal
+
+from test_framework.address import base58_to_byte
+from test_framework.blocktools import create_raw_transaction, create_tx_with_script
+from test_framework.key import ECKey
+from test_framework.messages import CTransaction, FromHex, ToHex, COIN
+from test_framework.mininode import P2PInterface, mininode_lock
+from test_framework.script import CScript, OP_TRUE, OP_FALSE, SignatureHashForkIdFromValues
+from test_framework.test_framework import BitcoinTestFramework
+from test_framework.util import (
+    assert_greater_than, assert_equal, assert_raises, connect_nodes, disconnect_nodes, wait_until, find_output
+)
+
+
+def getSighashes(prevOutput, spender, fundingtx):
+    return SignatureHashForkIdFromValues(
+        spender.txVersion,
+        spender.hashPrevOutputs,
+        spender.hashSequence,
+        prevOutput,
+        fundingtx.vout[0].scriptPubKey,
+        fundingtx.vout[0].nValue,
+        spender.outSequence,
+        spender.hashOutputs,
+        spender.lockTime,
+        spender.pushData[0][-1]  # last byte is hashType
+    )
+
+
+class DoubleSpendProofTest(BitcoinTestFramework):
+    def set_test_params(self):
+        # We need >= 2 nodes because submitting a double spend through a single
+        # node will still be refused before reaching mempool
+        self.num_nodes = 4
+        self.extra_args = [
+            ['-acceptnonstdtxn=1'],
+            ['-acceptnonstdtxn=1'],
+            ['-acceptnonstdtxn=1'],
+            ['-acceptnonstdtxn=1', '-doublespendproof=0']]
+
+    def skip_test_if_missing_module(self):
+        self.skip_if_no_wallet()
+
+    def getpubkey(self):
+        # we will spend a coinbase transaction from node[0] which was
+        # pre-mined for us by the framework to the deterministic privkey.
+        # We now construct a pubkey for that
+        base58privkey = self.nodes[0].get_deterministic_priv_key().key
+        privkeybytes, v = base58_to_byte(base58privkey)
+        privkey = ECKey()
+        privkey.set(privkeybytes[:-1], True)
+        return privkey.get_pubkey()
+
+    def run_test(self):
+        # create a p2p receiver
+        dspReceiver = P2PInterface()
+        self.nodes[0].add_p2p_connection(dspReceiver)
+        # workaround - nodes think they're in IBD unless one block is mined
+        self.nodes[0].generate(1)
+        self.sync_all()
+        # Disconnect the third node, will be used later for triple-spend
+        disconnect_nodes(self.nodes[1], self.nodes[2])
+        # Put fourth node (the non-dsproof-enabled node) with the connected group
+        # (we will check its log at the end to ensure it ignored dsproof inv's)
+        non_dsproof_node = self.nodes[3]
+        disconnect_nodes(self.nodes[2], non_dsproof_node)
+        connect_nodes(self.nodes[1], non_dsproof_node)
+
+        # Create and mine a regular non-coinbase transaction for spending
+        fundingtxid = self.nodes[0].getblock(self.nodes[0].getblockhash(1))['tx'][0]
+        fundingtx = FromHex(CTransaction(), self.nodes[0].getrawtransaction(fundingtxid))
+
+        # Create three conflicting transactions. They are only signed, but not yet submitted to the mempool
+        firstDSTx = create_raw_transaction(self.nodes[0], fundingtxid, self.nodes[0].getnewaddress(), 49.95)
+        secondDSTx = create_raw_transaction(self.nodes[0], fundingtxid, self.nodes[0].getnewaddress(), 49.95)
+        thirdDSTx = create_raw_transaction(self.nodes[0], fundingtxid, self.nodes[0].getnewaddress(), 49.95)
+
+        # Send the two conflicting transactions to the network
+        # Submit to two different nodes, because a node would simply reject
+        # a double spend submitted through RPC
+        firstDSTxId = self.nodes[0].sendrawtransaction(firstDSTx)
+        self.nodes[1].sendrawtransaction(secondDSTx)
+        wait_until(
+            lambda: dspReceiver.message_count["dsproof-beta"] == 1,
+            lock=mininode_lock,
+            timeout=25
+        )
+
+        # 1. The DSP message is well-formed and contains all fields
+        # If the message arrived and was deserialized successfully, then 1. is satisfied
+        dsp = dspReceiver.last_message["dsproof-beta"].dsproof
+        dsps = set()
+        dsps.add(dsp.serialize())
+
+        # Check that it is valid, both spends are signed with the same key
+        # NB: pushData is made of the sig + one last byte for hashtype
+        pubkey = self.getpubkey()
+        sighash1 = getSighashes(dsp.getPrevOutput(), dsp.spender1, fundingtx)
+        sighash2 = getSighashes(dsp.getPrevOutput(), dsp.spender2, fundingtx)
+        assert(pubkey.verify_ecdsa(dsp.spender1.pushData[0][:-1], sighash1))
+        assert(pubkey.verify_ecdsa(dsp.spender2.pushData[0][:-1], sighash2))
+
+        # 2. For p2pkh these is exactly one pushdata per spender
+        assert_equal(1, len(dsp.spender1.pushData))
+        assert_equal(1, len(dsp.spender2.pushData))
+
+        # 3. The two spenders are different, specifically the signature (push data) has to be different.
+        assert(dsp.spender1.pushData != dsp.spender2.pushData)
+
+        # 4. The first & double spenders are sorted with two hashes as keys.
+        assert(dsp.spender1.hashOutputs < dsp.spender2.hashOutputs)
+
+        # 5. The double spent output is still available in the UTXO database,
+        #    implying no spending transaction has been mined.
+        assert_equal(self.nodes[0].gettransaction(firstDSTxId)["confirmations"], 0)
+
+        # The original fundingtx is the same as the transaction being spent reported by the DSP
+        assert_equal(hex(dsp.prevTxId)[2:], fundingtxid)
+        assert_equal(dsp.prevOutIndex, 0)
+
+        # 6. No other valid proof is known.
+        #    IE if a valid proof is known, no new proofs will be constructed
+        #    We submit a _triple_ spend transaction to the third node
+        connect_nodes(self.nodes[0], self.nodes[2])
+        self.nodes[2].sendrawtransaction(thirdDSTx)
+        #    Await for a new dsp to be relayed to the node
+        #    if such a dsp (or the double or triple spending tx) arrives, the test fails
+        assert_raises(
+            AssertionError,
+            wait_until,
+            lambda: dspReceiver.message_count["dsproof-beta"] == 2 or dspReceiver.message_count["tx"] == 2,
+            lock=mininode_lock,
+            timeout=5
+        )
+
+        # Only P2PKH inputs are protected
+        # Check that a non-P2PKH output is not protected
+        self.nodes[0].generate(1)
+        fundingtxid = self.nodes[0].getblock(self.nodes[0].getblockhash(2))['tx'][0]
+        fundingtx = FromHex(CTransaction(), self.nodes[0].getrawtransaction(fundingtxid))
+        fundingtx.rehash()
+        nonP2PKHTx = create_tx_with_script(fundingtx, 0, b'', int(49.95 * COIN), CScript([OP_TRUE]))
+        signedNonP2PKHTx = self.nodes[0].signrawtransactionwithwallet(ToHex(nonP2PKHTx))
+        self.nodes[0].sendrawtransaction(signedNonP2PKHTx['hex'])
+        self.sync_all()
+
+        tx = FromHex(CTransaction(), signedNonP2PKHTx['hex'])
+        tx.rehash()
+
+        firstDSTx = create_tx_with_script(tx, 0, b'', int(49.90 * COIN), CScript([OP_TRUE]))
+        secondDSTx = create_tx_with_script(tx, 0, b'', int(49.90 * COIN), CScript([OP_FALSE]))
+
+        self.nodes[0].sendrawtransaction(ToHex(firstDSTx))
+        self.nodes[1].sendrawtransaction(ToHex(secondDSTx))
+
+        assert_raises(
+            AssertionError,
+            wait_until,
+            lambda: dspReceiver.message_count["dsproof-beta"] == 2,
+            lock=mininode_lock,
+            timeout=5
+        )
+
+        # Check that unconfirmed outputs are also protected
+        self.nodes[0].generate(1)
+        unconfirmedtx = self.nodes[0].sendtoaddress(self.nodes[0].getnewaddress(), 25)
+        self.sync_all()
+
+        firstDSTx = create_raw_transaction(self.nodes[0], unconfirmedtx, self.nodes[0].getnewaddress(), 24.9)
+        secondDSTx = create_raw_transaction(self.nodes[0], unconfirmedtx, self.nodes[0].getnewaddress(), 24.9)
+
+        self.nodes[0].sendrawtransaction(firstDSTx)
+        self.nodes[1].sendrawtransaction(secondDSTx)
+
+        wait_until(
+            lambda: dspReceiver.message_count["dsproof-beta"] == 2,
+            lock=mininode_lock,
+            timeout=5
+        )
+        dsp2 = dspReceiver.last_message["dsproof-beta"].dsproof
+        dsps.add(dsp2.serialize())
+        assert(len(dsps) == 2)
+
+        # Check that a double spent tx, which has some non-P2PKH inputs
+        # in its ancestor, still results in a dsproof being emitted.
+        self.nodes[0].generate(1)
+        # Create a 1-of-2 multisig address which will be an in-mempool
+        # ancestor to a double-spent tx
+        pubkey0 = self.nodes[0].getaddressinfo(
+            self.nodes[0].getnewaddress())['pubkey']
+        pubkey1 = self.nodes[1].getaddressinfo(
+            self.nodes[1].getnewaddress())['pubkey']
+        p2sh = self.nodes[0].addmultisigaddress(1, [pubkey0, pubkey1], "")['address']
+        # Fund the p2sh address
+        fundingtxid = self.nodes[0].sendtoaddress(p2sh, 49)
+        vout = find_output(self.nodes[0], fundingtxid, Decimal('49'))
+        self.sync_all()
+
+        # Spend from the P2SH to a P2PKH, which we will double spend from
+        # in the next step.
+        p2pkh1 = self.nodes[0].getnewaddress()
+        rawtx1 = create_raw_transaction(self.nodes[0], fundingtxid, p2pkh1, 48.999, vout)
+        signed_tx1 = self.nodes[0].signrawtransactionwithwallet(rawtx1)
+        txid1 = self.nodes[0].sendrawtransaction(signed_tx1['hex'])
+        vout1 = find_output(self.nodes[0], txid1, Decimal('48.999'))
+        self.sync_all()
+
+        # Now double spend the P2PKH which has a P2SH ancestor.
+        firstDSTx = create_raw_transaction(self.nodes[0], txid1, self.nodes[0].getnewaddress(), 48.9, vout1)
+        secondDSTx = create_raw_transaction(self.nodes[0], txid1, self.nodes[1].getnewaddress(), 48.9, vout1)
+        self.nodes[0].sendrawtransaction(firstDSTx)
+        self.nodes[1].sendrawtransaction(secondDSTx)
+
+        # We still get a dsproof, showing that not all ancestors have
+        # to be P2PKH.
+        wait_until(
+            lambda: dspReceiver.message_count["dsproof-beta"] == 3,
+            lock=mininode_lock,
+            timeout=5
+        )
+        dsp3 = dspReceiver.last_message["dsproof-beta"].dsproof
+        dsps.add(dsp3.serialize())
+        assert(len(dsps) == 3)
+
+        # Check that a double spent tx, which has some unconfirmed ANYONECANPAY
+        # transactions in its ancestry, still results in a dsproof being emitted.
+        self.nodes[0].generate(1)
+        fundingtxid = self.nodes[0].getblock(self.nodes[0].getblockhash(5))['tx'][0]
+        vout1 = find_output(self.nodes[0], fundingtxid, Decimal('50'))
+        addr = self.nodes[1].getnewaddress()
+        pubkey = self.nodes[1].getaddressinfo(addr)['pubkey']
+        inputs = [
+            {'txid': fundingtxid,
+             'vout': vout1, 'amount': 49.99,
+             'scriptPubKey': pubkey}
+        ]
+        outputs = {addr: 49.99}
+        rawtx = self.nodes[0].createrawtransaction(inputs, outputs)
+        signed = self.nodes[0].signrawtransactionwithwallet(rawtx,
+                                                            None,
+                                                            "NONE|FORKID|ANYONECANPAY")
+        assert 'complete' in signed
+        assert_equal(signed['complete'], True)
+        assert 'errors' not in signed
+        txid = self.nodes[0].sendrawtransaction(signed['hex'])
+        self.sync_all()
+        # The ANYONECANPAY is still unconfirmed, but let's create some
+        # double spends from it.
+        vout2 = find_output(self.nodes[0], txid, Decimal('49.99'))
+        firstDSTx = create_raw_transaction(self.nodes[1], txid, self.nodes[0].getnewaddress(), 49.98, vout2)
+        secondDSTx = create_raw_transaction(self.nodes[1], txid, self.nodes[1].getnewaddress(), 49.98, vout2)
+        self.nodes[0].sendrawtransaction(firstDSTx)
+        self.nodes[1].sendrawtransaction(secondDSTx)
+        # We get a dsproof.
+        wait_until(
+            lambda: dspReceiver.message_count["dsproof-beta"] == 4,
+            lock=mininode_lock,
+            timeout=5
+        )
+        dsp4 = dspReceiver.last_message["dsproof-beta"].dsproof
+        dsps.add(dsp4.serialize())
+        assert(len(dsps) == 4)
+
+        # Create a P2SH to double-spend directly (1-of-1 multisig)
+        self.nodes[0].generate(1)
+        self.sync_all()
+        pubkey2 = self.nodes[0].getaddressinfo(
+            self.nodes[0].getnewaddress())['pubkey']
+        p2sh = self.nodes[0].addmultisigaddress(1, [pubkey2,], "")['address']
+        fundingtxid = self.nodes[0].sendtoaddress(p2sh, 49)
+        vout = find_output(self.nodes[0], fundingtxid, Decimal('49'))
+        self.sync_all()
+        # Now double spend it
+        firstDSTx = create_raw_transaction(self.nodes[0], fundingtxid, self.nodes[0].getnewaddress(), 48.9, vout)
+        secondDSTx = create_raw_transaction(self.nodes[0], fundingtxid, self.nodes[1].getnewaddress(), 48.9, vout)
+        self.nodes[0].sendrawtransaction(firstDSTx)
+        self.nodes[1].sendrawtransaction(secondDSTx)
+        # No dsproof is generated.
+        assert_raises(
+            AssertionError,
+            wait_until,
+            lambda: dspReceiver.message_count["dsproof-beta"] == 5,
+            lock=mininode_lock,
+            timeout=5
+        )
+
+        # Check end conditions - still only 4 DSPs
+        last_dsp = dspReceiver.last_message["dsproof-beta"].dsproof
+        dsps.add(last_dsp.serialize())
+        assert(len(dsps) == 4)
+
+        # Finally, ensure that the non-dsproof node has the messages we expect in its log
+        # (this checks that dsproof was disabled for this node)
+        debug_log = os.path.join(non_dsproof_node.datadir, 'regtest', 'debug.log')
+        dsp_inv_ctr = 0
+        with open(debug_log, encoding='utf-8') as dl:
+            for line in dl.readlines():
+                if "Got DSProof INV" in line:
+                    # Ensure that if this node did see a dsproof inv, it explicitly ignored it
+                    assert "(ignored, -doublespendproof=0)" in line
+                    dsp_inv_ctr += 1
+                else:
+                    # Ensure this node is not processing dsproof messages and not requesting them via getdata
+                    assert "received: dsproof-beta" not in line and "Good DSP" not in line
+        # We expect it to have received at least some DSP inv broadcasts
+        assert_greater_than(dsp_inv_ctr, 0)
+
+
+if __name__ == '__main__':
+    DoubleSpendProofTest().main()
```

### test/functional/test_framework/blocktools.py
```diff
@@ -159,13 +159,14 @@ def create_transaction(node, txid, to_address, amount):
     return tx
 
 
-def create_raw_transaction(node, txid, to_address, amount):
-    """ Return raw signed transaction spending the first output of the
-        input txid. Note that the node must be able to sign for the
+def create_raw_transaction(node, txid, to_address, amount, vout=0):
+    """ Return raw signed transaction spending an output (the first
+        by default) output of the input txid.
+        Note that the node must be able to sign for the
         output that is being spent, and the node must not be running
         multiple wallets.
     """
-    inputs = [{"txid": txid, "vout": 0}]
+    inputs = [{"txid": txid, "vout": vout}]
     outputs = {to_address: amount}
     rawtx = node.createrawtransaction(inputs, outputs)
     signresult = node.signrawtransactionwithwallet(rawtx)
```

### test/functional/test_framework/messages.py
```diff
@@ -58,6 +58,7 @@
 MSG_BLOCK = 2
 MSG_CMPCTBLOCK = 4
 MSG_TYPE_MASK = 0xffffffff >> 2
+MSG_DSPROOF = 0x94a0 # Temporary type id
 
 # Serialization/deserialization tools
 
@@ -270,7 +271,8 @@ class CInv:
         0: "Error",
         1: "TX",
         2: "Block",
-        4: "CompactBlock"
+        4: "CompactBlock",
+        0x94a0: "DoubleSpendProofbeta"
     }
 
     def __init__(self, t=0, h=0):
@@ -589,6 +591,105 @@ def __repr__(self):
             self.nTime, self.nBits, self.nNonce, repr(self.vtx))
 
 
+class CDSProof:
+    __slots__ = ("prevTxId",
+                 "prevOutIndex",
+                 "spender1",
+                 "spender2")
+
+    def __init__(self, dsproof=None):
+        if dsproof is None:
+            self.prevTxId = None
+            self.prevOutIndex = 0
+            self.spender1 = CDSProofSpender()
+            self.spender2 = CDSProofSpender()
+        else:
+            self.prevTxId = dsproof.prevTxId
+            self.prevOutIndex = dsproof.prevOutIndex
+            self.spender1 = dsproof.spender1
+            self.spender2 = dsproof.spender2
+
+    def deserialize(self, f):
+        self.prevTxId = deser_uint256(f)
+        self.prevOutIndex = struct.unpack("<i", f.read(4))[0]
+        self.spender1 = CDSProofSpender()
+        self.spender1.deserialize(f)
+        self.spender2 = CDSProofSpender()
+        self.spender2.deserialize(f)
+
+    def serialize(self):
+        r = self.getPrevOutput()
+        r += self.spender1.serialize()
+        r += self.spender2.serialize()
+        return r
+
+    def getPrevOutput(self):
+        r = b""
+        r += ser_uint256(self.prevTxId)
+        r += struct.pack("<I", self.prevOutIndex)
+        return r
+
+    def __repr__(self):
+        return "CDSProof(prevTxId={:064x} prevOutIndex={}\nspender1={}\nspender2={})".format(
+            self.prevTxId, self.prevOutIndex, self.spender1, self.spender2)
+
+
+class CDSProofSpender:
+
+    __slots__ = ("txVersion",
+                 "outSequence",
+                 "lockTime",
+                 "hashPrevOutputs",
+                 "hashSequence",
+                 "hashOutputs",
+                 "pushData")
+
+    def __init__(self, spender=None):
+        if spender is None:
+            self.txVersion = 0
+            self.outSequence = 0
+            self.lockTime = 0
+            self.hashPrevOutputs = None
+            self.hashSequence = None
+            self.hashOutputs = None
+            self.pushData = []
+        else:
+            self.txVersion = spender.txVersion
+            self.outSequence = spender.outSequence
+            self.lockTime = spender.lockTime
+            self.hashPrevOutputs = spender.hashPrevOutputs
+            self.hashSequence = spender.hashSequence
+            self.hashOutputs = spender.hashOutputs
+            self.pushData = spender.pushData
+
+    def deserialize(self, f):
+        self.txVersion = struct.unpack("<i", f.read(4))[0]
+        self.outSequence = struct.unpack("<I", f.read(4))[0]
+        self.lockTime = struct.unpack("<I", f.read(4))[0]
+        self.hashPrevOutputs = deser_uint256(f)
+        self.hashSequence = deser_uint256(f)
+        self.hashOutputs = deser_uint256(f)
+        self.pushData = deser_string_vector(f)
+
+    def serialize(self):
+        r = b""
+        r += struct.pack("<i", self.txVersion)
+        r += struct.pack("<I", self.outSequence)
+        r += struct.pack("<I", self.lockTime)
+        r += ser_uint256(self.hashPrevOutputs)
+        r += ser_uint256(self.hashSequence)
+        r += ser_uint256(self.hashOutputs)
+        r += ser_string_vector(self.pushData)
+        return r
+
+    def pushDataToHex(self, data):
+        return "[" + ",".join(map(bytes.hex, data)) + "]"
+
+    def __repr__(self):
+        return "spender1txVersion={} spender1outSequence={} spender1lockTime={} spender1hashPrevOutputs={:064x} spender1hashSequence={:064x} spender1hashOutputs={:064x} spender1pushData={}".format(
+            self.txVersion, self.outSequence, self.lockTime, self.hashPrevOutputs, self.hashSequence, self.hashOutputs, self.pushDataToHex(self.pushData)
+        )
+
 class PrefilledTransaction:
     __slots__ = ("index", "tx")
 
@@ -1071,6 +1172,25 @@ def serialize(self):
     def __repr__(self):
         return "msg_block(block={})".format(repr(self.block))
 
+class msg_dsproof:
+    __slots__ = ("dsproof",)
+    command = b"dsproof-beta"
+
+    def __init__(self, dsproof=None):
+        if dsproof is None:
+            self.dsproof = CDSProof()
+        else:
+            self.dsproof = dsproof
+
+    def deserialize(self, f):
+        self.dsproof.deserialize(f)
+
+    def serialize(self):
+        return self.dsproof.serialize()
+
+    def __repr__(self):
+        return "msg_dsproof(dsproof-beta={})".format(repr(self.dsproof))
+
 
 # for cases where a user needs tighter control over what is sent over the wire
 # note that the user must supply the name of the command, and the data
```

### test/functional/test_framework/mininode.py
```diff
@@ -52,6 +52,7 @@
     msg_extversion,
     NODE_NETWORK,
     sha256,
+    msg_dsproof
 )
 from test_framework.util import wait_until
 
@@ -80,7 +81,8 @@
     b"tx": msg_tx,
     b"verack": msg_verack,
     b"version": msg_version,
-    b"extversion": msg_extversion
+    b"extversion": msg_extversion,
+    b"dsproof-beta": msg_dsproof,
 }
 
 MAGIC_BYTES = {
@@ -338,7 +340,8 @@ def on_message(self, message):
                 command = message.command.decode('ascii')
                 self.message_count[command] += 1
                 self.last_message[command] = message
-                getattr(self, 'on_' + command)(message)
+                command_no_hyphens = command.replace('-', '')
+                getattr(self, 'on_' + command_no_hyphens)(message)
             except Exception:
                 print("ERROR delivering {} ({})".format(
                     repr(message), sys.exc_info()[0]))
@@ -371,6 +374,8 @@ def on_getblocktxn(self, message): pass
 
     def on_getdata(self, message): pass
 
+    def on_dsproofbeta(self, message): pass
+
     def on_getheaders(self, message): pass
 
     def on_headers(self, message): pass
```

### test/functional/test_framework/script.py
```diff
@@ -734,16 +734,41 @@ def SignatureHashForkId(script, txTo, inIdx, hashtype, amount):
         serialize_outputs = txTo.vout[inIdx].serialize()
         hashOutputs = uint256_from_str(hash256(serialize_outputs))
 
+    return SignatureHashForkIdFromValues(
+        txTo.nVersion,
+        hashPrevouts,
+        hashSequence,
+        txTo.vin[inIdx].prevout.serialize(),
+        script,
+        amount,
+        txTo.vin[inIdx].nSequence,
+        hashOutputs,
+        txTo.nLockTime,
+        hashtype)
+
+
+def SignatureHashForkIdFromValues(
+        nVersion,
+        hashPrevouts,
+        hashSequence,
+        prevout,
+        script,
+        amount,
+        nSequence,
+        hashOutputs,
+        nLockTime,
+        hashtype):
+
     ss = bytes()
-    ss += struct.pack("<i", txTo.nVersion)
+    ss += struct.pack("<i", nVersion)
     ss += ser_uint256(hashPrevouts)
     ss += ser_uint256(hashSequence)
-    ss += txTo.vin[inIdx].prevout.serialize()
+    ss += prevout
     ss += ser_string(script)
     ss += struct.pack("<q", amount)
-    ss += struct.pack("<I", txTo.vin[inIdx].nSequence)
+    ss += struct.pack("<I", nSequence)
     ss += ser_uint256(hashOutputs)
-    ss += struct.pack("<i", txTo.nLockTime)
+    ss += struct.pack("<i", nLockTime)
     ss += struct.pack("<I", hashtype)
 
     return hash256(ss)
```
