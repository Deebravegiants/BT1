# [H] `BeefyAdapter`

## Summary
Severity: High
Contest weight: 0.8227
Dataset id: 18011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BeefyAdapter contract allows the vault owner to supply an optional _beefyBooster address during initialization. The code decodes this address from user‑controlled input but does not verify that the booster contract is a legitimate, endorsed Beefy booster. After decoding, the adapter unconditionally calls IERC20(_beefyVault).approve(_beefyBooster, type(uint256).max) when a non‑zero booster is provided, granting the booster an unlimited allowance to transfer the vault token held by the adapter. Later, during a deposit, the adapter calls beefyBooster.stake(beefyVault.balanceOf(address(this))). A malicious booster can implement the stake function to invoke _beefyVault.transferFrom(this, attacker, amount), using the previously granted allowance to move all tokens out of the adapter. The root cause is the absence of a validation step for the booster address and the reckless approval of an unlimited token allowance to an untrusted contract. Exploitation requires a malicious vault owner (or any actor able to set the booster) to deploy a contract that pretends to be a valid booster, passes its address in the initialization data, and then, when a user deposits funds, the booster drains those funds. The impact is that user deposits disappear, balances shown in the UI become zero, and no refunds are received, effectively stealing the assets stored in the adapter. This condition occurs whenever the adapter is initialized with a non‑zero booster that is not verified against the permission registry, and the deposit flow is executed. All users of the adapter, the protocol that relies on the adapter for asset management, and any token holders are affected. The issue was discovered during a security audit that highlighted the missing endorsement check and the unlimited approve pattern as a logical flaw. It can be hard to notice because granting an allowance to a contract is a common pattern and the stake call appears benign, masking the malicious behavior. To remediate, the adapter should enforce that the booster address is endorsed by the permission registry, reject boosters whose stakedToken does not match the vault, and avoid granting unlimited allowances; instead, use a minimal allowance or a pull‑based pattern, and consider removing the approve call entirely. This aligns the implementation with the intended business logic that only trusted Beefy boosters may manage deposited tokens, preserving accounting integrity and preventing unauthorized token transfers.

## Proof of Concept
When creating a BeefyAdapter, the vault owner can specify the `_beefyBooster`.

The current implementation does not check if the `_beefyBooster` is legitimate or not, and worse, it `_beefyVault.approve` to the `_beefyBooster` during initialization.

The code is as follows:
    
```solidity
contract BeefyAdapter is AdapterBase, WithRewards {
...
    function initialize(
        bytes memory adapterInitData,
        address registry,
        bytes memory beefyInitData
    ) external initializer {
       
        (address _beefyVault, address _beefyBooster) = abi.decode(
            beefyInitData,   //@audit <--------- beefyInitData comes from the owner's input: adapterData.data
            (address, address)
        );

        //@audit <-------- not check _beefyBooster is legal
        if (
            _beefyBooster != address(0) &&
            IBeefyBooster(_beefyBooster).stakedToken() != _beefyVault  
        ) revert InvalidBeefyBooster(_beefyBooster);   

...
      
        if (_beefyBooster != address(0))
            IERC20(_beefyVault).approve(_beefyBooster, type(uint256).max);     //@audit <---------  _beefyVault approve _beefyBooster    

}
    
    function _protocolDeposit(uint256 amount, uint256)
        internal
        virtual
        override
    {
        beefyVault.deposit(amount);
        if (address(beefyBooster) != address(0)) 
            beefyBooster.stake(beefyVault.balanceOf(address(this)));  //@audit <--------- A malicious beefyBooster can transfer the token
    }
```

As a result, a malicious user can pass a malicious `_beefyBooster` contract, and when the user deposits to the vault, the vault is saved to the `_beefyVault`.

This malicious `_beefyBooster` can execute `_beefyVault.transferFrom(BeefyAdapter)`, and take all the tokens stored by the adapter to `_beefyVault`.

## Recommendation
Check `_beefyBooster` just like you check `_beefyVault`:
    
```solidity
    function initialize(
        bytes memory adapterInitData,
        address registry,
        bytes memory beefyInitData
    ) external initializer {
...
        if (!IPermissionRegistry(registry).endorsed(_beefyVault))
            revert NotEndorsed(_beefyVault);
...            
        if (!IPermissionRegistry(registry).endorsed(_beefyBooster))
            revert NotEndorsed(_beefyBooster);

        if (
            _beefyBooster != address(0) &&
            IBeefyBooster(_beefyBooster).stakedToken() != _beefyVault
        ) revert InvalidBeefyBooster(_beefyBooster);
```
