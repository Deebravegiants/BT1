# [?] verifier.py: fix CVE-2012-2459: reject left-sibling duplicates

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-04-03
Source: https://github.com/spesmilo/electrum/commit/3d3907429422bdc053c94b260a9891fcdf13f9da
Type: security-commit

## Details
verifier.py: fix CVE-2012-2459: reject left-sibling duplicates

Due to how the txid-commitment merkle tree used in the block headers is constructed, we need an extra check to be able to validate the *position* of a txid in a block.

I think this is low severity for us.

See https://bitcointalk.org/?topic=102395 :

> The Merkle hash implementation that Bitcoin uses to calculate the Merkle
> root in a block header is flawed in that one can easily construct multiple
> lists of hashes that map to the same Merkle root.
> For example, merkle_hash([a, b, c]) and merkle_hash([a, b, c, c]) yield
> the same result. This is because, at every iteration, the Merkle hash
> function pads its intermediate list of hashes with the last hash if the
> list is of odd length, in order to make it of even length.
>
> And so, the Merkle root function can be effectively preimaged by
> changing the input so that one of the intermediate lists is of even
> length with the last two elements equal (where originally it was
> of odd length with a last element equal to the earlier mentioned two).
> As was later noted, this extends to any input length that is
> not a power of two:
> merkle_hash([a, b, c, d, e, f]) == merkle_hash([a, b, c, d, e, f, e, f]).
> Note that to maintain the same root hash, the only flexibility that
> exists is duplication of elements.

Ported from https://github.com/Electron-Cash/Electron-Cash/commit/165146362b4cb0ad74770b36aca1f9acb2800195

Co-authored-by: bitcoincashautist <80100588+A60AB5450353F40E@users.noreply.github.com>

## Patch
### electrum/verifier.py
```diff
@@ -43,6 +43,7 @@ class MerkleVerificationFailure(Exception): pass
 class MissingBlockHeader(MerkleVerificationFailure): pass
 class MerkleRootMismatch(MerkleVerificationFailure): pass
 class InnerNodeOfSpvProofIsValidTx(MerkleVerificationFailure): pass
+class LeftSiblingDuplicate(MerkleVerificationFailure): pass
 
 
 class SPV(NetworkJobOnDefaultServer):
@@ -149,11 +150,16 @@ def hash_merkle_root(cls, merkle_branch: Sequence[str], tx_hash: str, leaf_pos_i
         if leaf_pos_in_tree < 0:
             raise MerkleVerificationFailure('leaf_pos_in_tree must be non-negative')
         index = leaf_pos_in_tree
-        for item in merkle_branch_bytes:
-            if len(item) != 32:
+        for sibling in merkle_branch_bytes:
+            if len(sibling) != 32:
                 raise MerkleVerificationFailure('all merkle branch items have to be 32 bytes long')
-            inner_node = (item + h) if (index & 1) else (h + item)
+            is_right_child = (index & 1)
+            inner_node = (sibling + h) if is_right_child else (h + sibling)
+            # CVE-2017-12842 protection: inner node must not be a valid tx
             cls._raise_if_valid_tx(inner_node.hex())
+            # CVE-2012-2459 protection: reject left-sibling duplicates
+            if is_right_child and sibling == h:
+                raise LeftSiblingDuplicate()
             h = sha256d(inner_node)
             index >>= 1
         if index != 0:
@@ -162,7 +168,7 @@ def hash_merkle_root(cls, merkle_branch: Sequence[str], tx_hash: str, leaf_pos_i
 
     @classmethod
     def _raise_if_valid_tx(cls, raw_tx: str):
-        # If an inner node of the merkle proof is also a valid tx, chances are, this is an attack.
+        # CVE-2017-12842: If an inner node of the merkle proof is also a valid tx, chances are, this is an attack.
         # https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-June/016105.html
         # https://lists.linuxfoundation.org/pipermail/bitcoin-dev/attachments/20180609/9f4f5b1f/attachment-0001.pdf
         # https://bitcoin.stackexchange.com/questions/76121/how-is-the-leaf-node-weakness-in-merkle-trees-exploitable/76122#76122
```

### tests/test_verifier.py
```diff
@@ -3,49 +3,123 @@
 from electrum.bitcoin import hash_encode
 from electrum.transaction import Transaction
 from electrum.util import bfh
-from electrum.verifier import SPV, InnerNodeOfSpvProofIsValidTx
+from electrum.verifier import SPV, InnerNodeOfSpvProofIsValidTx, LeftSiblingDuplicate
 
 from . import ElectrumTestCase
 
 
-MERKLE_BRANCH = [
-    'f2994fd4546086b21b4916b76cf901afb5c4db1c3ecbfc91d6f4cae1186dfe12',
-    '6b65935528311901c7acda7db817bd6e3ce2f05d1c62c385b7caadb65fac7520']
-
-MERKLE_ROOT = '11dbac015b6969ea75509dd1250f33c04ec4d562c2d895de139a65f62f808254'
-
-VALID_64_BYTE_TX = ('0200000001cb659c5528311901a7aada7db817bd6e3ce2f05d1c62c385b7caad'
-                    'b65fac75201234000000fabcdefa01abcd1234010000000405060708fabcdefa')
-assert len(VALID_64_BYTE_TX) == 128
-
-
-class VerifierTestCase(ElectrumTestCase):
-    # these tests are regarding the attack described in
+class TestVerifier_CVE_2017_12842(ElectrumTestCase):
+    # these tests are regarding CVE-2017-12842, the attack described in
     # https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2018-June/016105.html
     TESTNET = True
 
+    MERKLE_BRANCH = [
+        'f2994fd4546086b21b4916b76cf901afb5c4db1c3ecbfc91d6f4cae1186dfe12',
+        '6b65935528311901c7acda7db817bd6e3ce2f05d1c62c385b7caadb65fac7520',
+    ]
+    MERKLE_ROOT = '11dbac015b6969ea75509dd1250f33c04ec4d562c2d895de139a65f62f808254'
+    VALID_64_BYTE_TX = ('0200000001cb659c5528311901a7aada7db817bd6e3ce2f05d1c62c385b7caad'
+                        'b65fac75201234000000fabcdefa01abcd1234010000000405060708fabcdefa')
+    assert len(VALID_64_BYTE_TX) == 128
+
     def test_verify_ok_t_tx(self):
         """Actually mined 64 byte tx should not raise."""
-        t_tx = Transaction(VALID_64_BYTE_TX)
+        t_tx = Transaction(self.VALID_64_BYTE_TX)
         t_tx_hash = t_tx.txid()
-        self.assertEqual(MERKLE_ROOT, SPV.hash_merkle_root(MERKLE_BRANCH, t_tx_hash, 3))
+        self.assertEqual(self.MERKLE_ROOT, SPV.hash_merkle_root(self.MERKLE_BRANCH, t_tx_hash, 3))
 
     def test_verify_fail_f_tx_odd(self):
         """Raise if inner node of merkle branch is valid tx. ('odd' fake leaf position)"""
         # first 32 bytes of T encoded as hash
-        fake_branch_node = hash_encode(bfh(VALID_64_BYTE_TX[:64]))
-        fake_mbranch = [fake_branch_node] + MERKLE_BRANCH
+        fake_branch_node = hash_encode(bfh(self.VALID_64_BYTE_TX[:64]))
+        fake_mbranch = [fake_branch_node] + self.MERKLE_BRANCH
         # last 32 bytes of T encoded as hash
-        f_tx_hash = hash_encode(bfh(VALID_64_BYTE_TX[64:]))
+        f_tx_hash = hash_encode(bfh(self.VALID_64_BYTE_TX[64:]))
         with self.assertRaises(InnerNodeOfSpvProofIsValidTx):
             SPV.hash_merkle_root(fake_mbranch, f_tx_hash, 7)
 
     def test_verify_fail_f_tx_even(self):
         """Raise if inner node of merkle branch is valid tx. ('even' fake leaf position)"""
         # last 32 bytes of T encoded as hash
-        fake_branch_node = hash_encode(bfh(VALID_64_BYTE_TX[64:]))
-        fake_mbranch = [fake_branch_node] + MERKLE_BRANCH
+        fake_branch_node = hash_encode(bfh(self.VALID_64_BYTE_TX[64:]))
+        fake_mbranch = [fake_branch_node] + self.MERKLE_BRANCH
         # first 32 bytes of T encoded as hash
-        f_tx_hash = hash_encode(bfh(VALID_64_BYTE_TX[:64]))
+        f_tx_hash = hash_encode(bfh(self.VALID_64_BYTE_TX[:64]))
         with self.assertRaises(InnerNodeOfSpvProofIsValidTx):
             SPV.hash_merkle_root(fake_mbranch, f_tx_hash, 6)
+
+
+class TestVerifier_CVE_2012_2459(ElectrumTestCase):
+    # These tests are regarding CVE-2012-2459.
+    # Bitcoin's Merkle tree duplicates odd nodes to balance the tree. An attacker can
+    # exploit this by constructing a tree where a duplicated subtree is treated
+    # as containing real leaves, allowing forged proofs for phantom leaf positions.
+    #
+    # Example with 11 real leaves and forged 16-leaf claim:
+    #
+    # Real tree (11 leaves):
+    #
+    #                           **root**
+    #                   __________/  \_________
+    #                  /                       \
+    #                 14                        c       Height 3
+    #             _ /   \ _                    / \
+    #           /           \                 /   \
+    #          6             13              b     b'   Height 2
+    #        /    \        /    \         /     \
+    #       2      5      9      12      17      a      Height 1
+    #      / \    / \    / \    /  \    /  \    /  \
+    #     0   1  3   4  7   8  10  11  15  16  18  18'  Height 0
+    #     --------------------------------------------------------
+    #     0   1  2   3  4   5   6   7   8   9  10       Leaf index
+    #
+    #     Nodes marked with ' are duplicates to balance the tree.
+    #
+    # Forged tree (attacker claims 16 leaves):
+    #
+    #                           **root**
+    #                   __________/  \________________
+    #                  /                              \
+    #                 14                              c                   Height 3
+    #             _ /   \ _                    _____/   \_____
+    #           /           \                 /               \
+    #          6             13              b                 b'         Height 2
+    #        /    \        /    \         /     \           /     \
+    #       2      5      9      12      17      a        17'      a'     Height 1
+    #      / \    / \    / \    /  \    /  \    /  \     /  \     /  \
+    #     0   1  3   4  7   8  10  11  15  16  18  18'  15' 16'  18' 18'  Height 0
+    #     --------------------------------------------------------------------------
+    #     0   1  2   3  4   5   6   7   8   9  10  11!  12! 13!  14! 15!  Leaf index
+    #
+    #     Nodes with ! are phantom leaves. The attacker duplicated the entire
+    #     subtree under 'b' to create fake leaves 11-15.
+    #
+    # The attack works because:
+    #   - Real proof for leaf 10:   [18', 17 , b', 14] with b' as RIGHT sibling
+    #   - Forged proof for leaf 14: [18', 17', b , 14] with b as LEFT sibling
+    #
+    # We can guard against this: in forged proofs, a duplicate will appear as a LEFT sibling
+    # (sibling == current when index bit is 1).
+    # Legitimate duplicates for balancing only appear as RIGHT siblings.
+    TESTNET = True
+
+    # from testnet3 block 4909055 (https://blockstream.info/testnet/block/00000000c4a54b073c224bbf1f7c40cc85498a823e1dd5d20be51e6464a3dab9)
+    # but even if it gets reorged, point is:
+    # - block has 3 txns total, so valid indices [0,1,2]
+    # - next power of 2 is 4, so merkle tree leaves will be [t0,t1,t2,t2']
+    # - TXID is for t2, so its real index is 2, but index 3 could be "forged" for it as well
+    MERKLE_BRANCH = [
+        '9b2c7e407188465594832cfbe84c9758029084527c855ea29a16603e5d1c51b6',
+        'a8484ccbaa74ffa060d0a500f7ce3ea4953beace18df8384024dfa9290385b1c',
+    ]
+    MERKLE_ROOT = '3465af659f6438b133c6d980accbb61b7be43f8ad899e40054e33b37aecba28e'
+    TXID = '9b2c7e407188465594832cfbe84c9758029084527c855ea29a16603e5d1c51b6'
+
+    def test_valid_right_sibling_duplicate(self):
+        leaf_pos_in_tree = 2
+        self.assertEqual(self.MERKLE_ROOT, SPV.hash_merkle_root(self.MERKLE_BRANCH, self.TXID, leaf_pos_in_tree))
+
+    def test_malicious_left_sibling_duplicate(self):
+        leaf_pos_in_tree = 3
+        with self.assertRaises(LeftSiblingDuplicate):
+            SPV.hash_merkle_root(self.MERKLE_BRANCH, self.TXID, leaf_pos_in_tree)
```
