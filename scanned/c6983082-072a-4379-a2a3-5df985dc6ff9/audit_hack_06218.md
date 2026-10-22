# [H] Price manipulation can lead to users lossing funds

## Summary
Severity: High
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L219-L222
Type: audit-issue

## Details
# Price manipulation can lead to users lossing funds

## Summary
Early malicious user will profit from future users' deposits while future users' will loose funds/value.


## Vulnerability Detail

An early user can call the deposit function of  vaults with only 1 wei of the asset and respectively get 1 wei of the shares in return. After that the attacker may send `10000 * 10 ** 18 wei` of the asset to inflate the share price from `1 to 1 * 10 ** 22 ((1 + 10000e18 - 1) / 1)`  The next user who deposits some amount of asset will receive significatly less shares - if the next user deposits `20000 * 10 ** 18` wei of the asset they will receive only 2 wei of shares which means they have lost half of their money if they claim right after that.


## Impact


```vyper
contracts/Vault.vy:
  226  
  227: @nonreentrant("lock")
  228: @external
  229: def register_deposit(_token_id: uint256, _amount: uint256):
  230:   
  231:     assert self.is_depositor[msg.sender], "not allowed"
  232:     assert self._is_valid_token_id(_token_id)
  233: 
  234:     position: Position = self.positions[_token_id]
  235:     assert position.is_liquidated == False, "position already liquidated"
  236: 
  237:     position.token_id = _token_id
  238:     position.amount_deposited += _amount
  239: 
  240:     # transfer WETH to self
  241:     ERC20(WETH).transferFrom(msg.sender, self, _amount)
  242: 
  243:     # deposit WETH to Alchemix
  244:     shares_issued: uint256 = self._deposit_to_alchemist(_amount)
  245:     position.shares_owned += shares_issued
  246:     self.total_shares += shares_issued
  247:     
  248:     self.positions[_token_id] = position
  249: 
  250:     # mint alchemix debt to fund_receiver
  251:     amount_to_mint: uint256 = self._calculate_amount_to_mint(shares_issued)
  252:     assert amount_to_mint > 0, "cannot mint new Alchemix debt" 
  253: 
  254:     self._mint_from_alchemix(amount_to_mint, self.fund_receiver)
  255: 
  256:     log Deposit(msg.sender, _token_id, _amount)

```

## Code Snippet
[Vault.vy#L219-L222](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L219-L222)


## Tool used

Manual Review

## Recommendation

When creating the vault add initial funds in order to make it harder to inflate the price.
Best practice would add initial funds as part of the initialization of the contract (to prevent front-running).
