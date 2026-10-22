# [M] Multiples initializations of `JBTiered721Delegate`

## Summary
Severity: Medium
Contest weight: 0.5346
Dataset id: 16970
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `initialize` method of the `JBTiered721Delegate` contract has as a flag that the `_store` argument is different from `address(0)`, however, it can be initialized by anyone with this value to allow the project to continue with its usual initialization, the attacker could have interfered and modified the corresponding values to carry out an attack.

## Proof of Concept
```solidity
function initialize(
  uint256 _projectId,
  IJBDirectory _directory,
  string memory _name,
  string memory _symbol,
  IJBFundingCycleStore _fundingCycleStore,
  string memory _baseUri,
  IJBTokenUriResolver _tokenUriResolver,
  string memory _contractUri,
  JB721PricingParams memory _pricing,
  IJBTiered721DelegateStore _store,
  JBTiered721Flags memory _flags
) public override {
  // Make the original un-initializable.
  require(address(this) != codeOrigin);
  // Stop re-initialization.
  require(address(store) == address(0));

  // Initialize the sub class.
  JB721Delegate._initialize(_projectId, _directory, _name, _symbol);

  fundingCycleStore = _fundingCycleStore;
  store = _store;
  pricingCurrency = _pricing.currency;
  pricingDecimals = _pricing.decimals;
  prices = _pricing.prices;

  // Store the base URI if provided.
  if (bytes(_baseUri).length != 0) _store.recordSetBaseUri(_baseUri);

  // Set the contract URI if provided.
  if (bytes(_contractUri).length != 0) _store.recordSetContractUri(_contractUri);

  // Set the token URI resolver if provided.
  if (_tokenUriResolver != IJBTokenUriResolver(address(0)))
    _store.recordSetTokenUriResolver(_tokenUriResolver);

  // Record adding the provided tiers.
  if (_pricing.tiers.length > 0) _store.recordAddTiers(_pricing.tiers);

  // Set the flags if needed.
  if (
    _flags.lockReservedTokenChanges ||
    _flags.lockVotingUnitChanges ||
    _flags.lockManualMintingChanges ||
    _flags.pausable
  ) _store.recordFlags(_flags);

  // Transfer ownership to the initializer.
  _transferOwnership(msg.sender);
}
```

So if the attacker initializes the contract as follows:

  * `_baseUri` = ""
  * `_contractUri` = ""
  * `_tokenUriResolver` = `address(0)`
  * `_pricing.tiers` = []
  * `_flags` = all `false`

The contract will be initialized and transfered the ownership to `msg.sender`.

After that, the owner can call `didPay` with the the fake data provided in [JBTiered721Delegate.sol:221](https://github.com/jbx-protocol/juice-nft-rewards/blob/f9893b1497098241dd3a664956d8016ff0d0efd0/contracts/JBTiered721Delegate.sol#L221) and increase `creditsOf` of anyone [JBTiered721Delegate.sol:587](https://github.com/jbx-protocol/juice-nft-rewards/blob/f9893b1497098241dd3a664956d8016ff0d0efd0/contracts/JBTiered721Delegate.sol#L587) without touching any `store` call.

  * The attacker can transfer the ownership to the contract, and the project will be able to initialize the contract again without notice.

## Recommendation
Ensure that the `store` address is not empty.

I believe the finding to be valid if:
 
  * the attacker initialize the contract with `_store == address(0)` and the parameters as above so it does not revert in the normal process
  * the attacker calls initialize to transfer the ownership to himself and modify the storage so he can then call `didPay`
  * the attacker calls `didPay` to manipulate `creditsOf`
  * finally the attacker calls `initialize` to set `_store` to non zero and at this point it is like if nothing happened although `creditsOf` has been manipulated

Hmm, this would require a spoof directory too (to bypass the isTerminalOf check) -> I’d mitigate with a `check msg.value==data.value` in the abstract delegate contract, ie if someone wants to do this, actually paying the credit is needed

Def nice finding, ggwp!

I do agree that Med is more appropriate as it falls within centralization risks as ultimately only the deployer could exploit this.
