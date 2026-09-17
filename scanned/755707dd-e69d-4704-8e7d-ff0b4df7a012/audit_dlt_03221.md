# [M] User voting power is not synchronized after multiplier changes

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/283
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/NFTBoostVault.sol#L363-#L371


# Vulnerability details

## Impact
- User voting power is not synchronized after multiplier changes
- If manager decrease multiplier for a token, users voting power will not be affected

## Proof of Concept
Currently the function `setMultiplier` of contract `NFTBoostVault` is implemented as follows:
```solidity
    function setMultiplier(address tokenAddress, uint128 tokenId, uint128 multiplierValue) public override onlyManager {
        if (multiplierValue > MAX_MULTIPLIER) revert NBV_MultiplierLimit();

        NFTBoostVaultStorage.AddressUintUint storage multiplierData = _getMultipliers()[tokenAddress][tokenId];
        // set multiplier value
        multiplierData.multiplier = multiplierValue;

        emit MultiplierSet(tokenAddress, tokenId, multiplierValue);
    }
```

The problem with this code is that it does not update the users voting power, even though their multiplier has changed. The contract did provide a function called `updateVotingPower` to update users voting power as follows:
```solidity
    function updateVotingPower(address[] calldata userAddresses) public override {
        if (userAddresses.length > 50) revert NBV_ArrayTooManyElements();

        for (uint256 i = 0; i < userAddresses.length; ++i) {
            NFTBoostVaultStorage.Registration storage registration = _getRegistrations()[userAddresses[i]];
            _syncVotingPower(userAddresses[i], registration);
        }
    }
```
We can argue that the manager can call this function to update users voting power after they change multiplier; however, there are multiple problems with this solution:
- The input of `updateVotingPower` is a list of user adresses, so the manager must have map of token id to a list of users using that token id as their multiplier. However, this data is not saved in the contract. When users register, their registrations are tracked using a variable of type `map(address => NFTBoostVaultStorage.Registration)`. I've looked into the contracts and found no way to retrieve a list of users associated with a token id, even function `_registerAndDelegate` does not emit an event showing which ERC1155 tokenId the users use at registration time.
- Function `updateVotingPower` only allow updating 50 addresses at a time, so if there are many users associated with a particular token ids, they have more time to try front running the manager.

Below is a POC for this issue, place this file under `test` folder with name `VotingPowerNotUpdatedAfterMultiplierChange.ts` and run it using command:
`npx hardhat test test/VotingPowerNotUpdatedAfterMultiplierChange.ts`

The flow of this POC is as follows:
- Alice is minted a reputation badge
- The reputation badge is then set a multiplier by nft boost vault manager
- Alice uses this reputation badge to boost her voting power
- After the manager changes Alice's badge multiplier, her voting power is unchanged.

```typescript
import { expect } from "chai";
import { constants } from "ethers";
import { ethers, waffle } from "hardhat";

import { deploy } from "./utils/deploy";
import { TestContextGovernance, governanceFixture } from "./utils/governanceFixture";
import { TestContextToken, tokenFixture } from "./utils/tokenFixture";

const { provider, loadFixture } = waffle;
import {
	ArcadeToken,
	ArcadeTreasury,
	CoreVoting,
	LockingVault,
	NFTBoostVault,
	VestingVault,
	ArcadeTokenDistributor,
	ARCDVestingVault,
	FeeController, MockERC1155, PromissoryNote,
	ReputationBadge,
	IReputationBadge,
	IBadgeDescriptor
 } from "../../src/types";

 import { BlockchainTime } from "./utils/time";
 import { MerkleTree } from "merkletreejs";
import { BADGE_MANAGER_ROLE } from "./utils/constants";


/**
 * nft boost vault test
 */

describe("Governance operations with nft boost voting vault", async () => {

	const ONE = ethers.utils.parseEther("1");
	const MULTIPLIER_DENOMINATOR = 1e3;
	const MAX = ethers.constants.MaxUint256;
	

	let signers: SignerWithAddress[];

	let alice: Signer;

	let arcdToken: ArcadeToken;
	let arcdVestingVault: ARCDVestingVault;
	let deployer: Signer;
	let arcdDst: ArcadeTokenDistributor;

	let reputationBadge: ReputationBadge;
	let nftBoostVault: NFTBoostVault;


	let feeController: FeeController;

	let coreVoting: CoreVoting;

	let blockchainTime: BlockchainTime;

	let descriptor: IBadgeDescriptor;

	beforeEach( async function () {

		// get signers
		signers = await ethers.getSigners();
		alice = signers[6];
		deployer = signers[0];


		// tree data for two tokens
        let recipientsTokenId = [{
                address: alice.address,
                tokenId: 1,
                amount: 1,
        }];

        let merkleTrieTokenId = await getMerkleTree(recipientsTokenId);
        let rootTokenId = merkleTrieTokenId.getHexRoot();

        let proofAlice = merkleTrieTokenId.getHexProof(
            ethers.utils.solidityKeccak256(
                ["address", "uint256", "uint256"],
                [alice.address, 1, 1],
            ),
        );

        // deploy descriptor contract
        descriptor = <IBadgeDescriptor>await deploy("BadgeDescriptor", deployer, ["https://www.domain.com/"]);
        await descriptor.deployed();
        // Deploy reputation badge

        reputationBadge = <IReputationBadge>await deploy("ReputationBadge", deployer, [deployer.address, descriptor.address]);
        await reputationBadge.deployed();
        await reputationBadge.connect(deployer).grantRole(BADGE_MANAGER_ROLE, deployer.address);


        // Deployer set expiration time
        let blockchainTime = new BlockchainTime();
        let expiration = await blockchainTime.secondsFromNow(3600); // 1 hour
        await reputationBadge.connect(deployer).publishRoots([{
        	tokenId:1,
        	claimRoot: rootTokenId,
        	claimExpiration: expiration,
        	mintPrice: 0
        }]);
        //Alice mint tokenId
        await reputationBadge.connect(alice).mint(alice.address, 1, 1, 1, proofAlice);



		// deploy arcade token distributor
		arcdDst = <ArcadeTokenDistributor> await deploy(
			"ArcadeTokenDistributor",
			signers[0],
			[]
		);
		await arcdDst.deployed();

		// Deploy arcade token
		arcdToken = <ArcadeToken> await deploy(
			"ArcadeToken",
			signers[0],
			[
				deployer.address,
				arcdDst.address
			]
		);
		await arcdToken.deployed();

		// set arcade token as token for arcade distribution
		await arcdDst.connect(deployer).setToken(arcdToken.address);

		// mint tokens take tokens from the distributor for use in tests
		await arcdDst.connect(deployer).toPartnerVesting(signers[0].address);

		// transfer tokens to signers and approve locking vault to spend

		for (let i = 0; i< signers.length; i++){
			await arcdToken.connect(deployer).transfer(signers[i].address, ONE.mul(100));
		}

		// Deploy nft boost vault
		let staleBlockNum = 0;
		nftBoostVault = <NFTBoostVault>await deploy("NFTBoostVault", signers[0], [
            arcdToken.address,
            staleBlockNum,
            deployer.address, // timelock address who can update the manager
            deployer.address, // manager address who can update multiplier values
        ]);
        await nftBoostVault.deployed();


	});

	it("Voting power is not updated after multiplier change", async () => {

		// Add multiplier for reputation badge token id = 1
		// Multiplier is 1400
		await nftBoostVault.connect(deployer).setMultiplier(reputationBadge.address,1, 1400);

		// Confirm that alice is holding the token
		expect(await reputationBadge.balanceOf(alice.address, 1)).to.equal(1);

		// Alice add nft id =1 to nft boost vault
		await arcdToken.connect(alice).approve(nftBoostVault.address, ONE);
		await reputationBadge.connect(alice).setApprovalForAll(nftBoostVault.address, true);

		const tx = await nftBoostVault.connect(alice).addNftAndDelegate(ONE, 1, reputationBadge.address, alice.address);
		const votingPowerBefore = await nftBoostVault.queryVotePowerView(alice.address, tx.blockNumber);

		// Alice voting power is the amount * multiplier
		expect(votingPowerBefore).to.be.eq(ONE.mul(1400).div(MULTIPLIER_DENOMINATOR));


		// Now the manager reduce the token's multiplier to 1200
		await nftBoostVault.connect(deployer).setMultiplier(reputationBadge.address,1, 1200);
		expect(await nftBoostVault.getMultiplier(reputationBadge.address, 1), 1200);


		// Get current block
		let blockchainTime = new BlockchainTime();
        let nowBlock = await blockchainTime.secondsFromNow(0); // 1 hour
        
        // Alice voting power is unchanged
		const votingPowerAfter = await nftBoostVault.queryVotePowerView(alice.address, nowBlock);
		expect(votingPowerBefore).to.be.eq(votingPowerAfter);

	});

	async function getMerkleTree(accounts: Account[]) {
	    const leaves = await Promise.all(accounts.map(account => hashAccount(account)));
	    return new MerkleTree(leaves, keccak256Custom, {
	        hashLeaves: false,
	        sortPairs: true,
	    });
	}

	async function hashAccount(account: Account) {
	    return ethers.utils.solidityKeccak256(
	        ["address", "uint256", "uint256"],
	        [account.address, account.tokenId, account.amount],
	    );
	}

	function keccak256Custom(bytes: Buffer) {
	    const buffHash = ethers.utils.solidityKeccak256(["bytes"], ["0x" + bytes.toString("hex")]);
	    return Buffer.from(buffHash.slice(2), "hex");
	}


});
```

## Tools Used
Manual review

## Recommended Mitigation Steps
I recommend creating a map of token id to a list of users using that token as multiplier and synchronize their voting power in function `setMultiplier`





## Assessed type

Other
