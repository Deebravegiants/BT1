# [H] Immunefi: Top 3 Bugs from the ThunderNFT Invite Only Program

## Summary
Severity: High
Published: Wed, 18 Dec 2024
Source: https://medium.com/immunefi/top-3-bugs-from-the-thundernft-invite-only-program-373da9824cc9?source=rss----6cdc579be8a0---4
Type: security-research

## Details
## ⚠️ THIS ARTICLE HAS MOVED

 This Medium version is archived and is no longer being updated. 

 Read the current and maintained version on the Immunefi Blog. 

 From 12th August to 2nd September 2024, the ThunderNFT protocol hosted an Invite-Only Program (IOP) on the Immunefi platform for researchers to hunt on code for their unique NFT marketplace on Fuel, an L2 on Ethereum that utilizes Fuel VM.

 An IOP is a form of Audit Competition which is exclusively accessible to a select group of security researchers, and in this case, they consist of researchers who have submitted at least 1 valid report during the Fuel Attackathon event.

 A total of 12 researchers were invited to compete, and 41 valid reports were rewarded from a pool of $65,000 USDC.

 Here are the top three findings from the Shardeum Ancillaries audit competition, as identified by the Immunefi team. As of this publication, all vulnerabilities have been FIXED.

## 1. Insufficient validation in order modifications leading to the theft of NFTs — 34980

 - Finder: Solosync6 

- Severity: Critical

- Asset: https://github.com/ThunderFuel/smart-contracts/blob/main/contracts-v1/thunder_exchange/src/main.sw 

 The contract includes a functionality that allows users to update their orders from the buying side to the selling side using the update_order(…) function. However, a vulnerability exists in the update_order(…) function due to insufficient validation of NFT ownership.

 https://medium.com/media/029d8b59e4e3cb732aa7df7361c7e4ed/href It is important to note that switching sides is permitted within _validate_maker_order_input .

 However, critically, there is no validation to ensure that the attacker actually owns the NFT when the order side is changed. This flaw enables a user to set a sell order for an arbitrary NFT without properly verifying ownership.

 https://medium.com/media/ba2257284fe9ba7e980cdb4fb8071973/href On cancellation, the NFT asset is transferred back to the maker, only this time, the maker was never the original owner of the NFT.

 An attacker can exploit this by calling the cancel_order(…) function. During the cancellation process, the contract relies on the strategy contract to return the correct order information without performing additional ownership verification. This allows the attacker to transfer an arbitrary NFT to themselves, resulting in the theft of the NFT.

### PoC and Exploit Steps:

 - Create buy orders for valuable NFTs they do not own.

- Convert these buy orders into sell orders without actually owning the NFTs.

- Cancel these “sell” orders, potentially gaining possession of NFTs they never owned.

 Here is a test case that showcases the above exploit.

 https://medium.com/media/6e2c5ee5c630006c4b952c08f2c2cab2/href 
## 2. Hardcoded Logic in Execution Result Library Leads to Maker Losses — 34534

 - Finder: NinetyNineCrits 

- Severity: Critical

- Asset: https://github.com/ThunderFuel/smart-contracts/blob/main/contracts-v1/libraries/src/execution_result.sw 

 The project allows makers to specify the desired quantity of an assetId through the MakerOrder struct as shown below.

 https://medium.com/media/345dc4a8c2b03cb6a736ad02a0ad5cad/href However, when an order is fulfilled, the maker receives only a single unit of the assetId regardless of the specified quantity. Despite this, they are charged the full price for the order due to a hardcoded value in the contract.

 When a taker fulfills a maker’s order, the _execute_sell_taker_order function verifies that the taker has sent the required amount of tokens as part of the transaction call:

 https://medium.com/media/9b242cf1c970d1929db8d3a130369198/href Currently, execution_result.amount is hardcoded to 1, meaning the maker always receives only 1 unit of the specified tokenId, regardless of the quantity requested. This mismatch results in unexpected losses for the maker.

 https://medium.com/media/0d812e6e3bc31159d07d0420468e3af1/href For ERC1155 tokens, the maker always receives only 1 unit of the specified tokenId, regardless of the requested quantity, resulting in unexpected losses.

### PoC and Exploit steps:

 - Deploy and initialize all project contracts, ensuring proper references between them.

- Deploy a simple ERC1155 contract that allows arbitrary token minting.

- The taker (seller) mints 10 tokens for themselves.

- The maker (buyer) places an order for 10 units of the same AssetId minted by the taker.

- The taker fills the order but transfers only 1 unit (the transaction fails if more units are transferred).

- Verify that the maker received only 1 unit of the ERC1155 token instead of the requested 10 units.

 Here is a test case that showcases the above exploit.

 https://medium.com/media/1368647d21c5143ac72f70c69a1819e5/href 
## 3. Flawed Logic in ThunderExchange: NFT Owners with Sell Order Blocked from Accepting Bids — 34714

 - Finder: zeroK 

- Severity: Medium

- Asset: https://github.com/ThunderFuel/smart-contracts/blob/main/contracts-v1/thunder_exchange/src/main.sw 

 The _execute_sell_taker_order function validates msg_asset() when the user calls the execute_order function, making it impossible for the NFT seller to accept any bids.

 This is because the place_order function requires the seller to transfer the NFT to the Thunder Exchange, leaving the seller without the asset_id (the NFT).

 https://medium.com/media/8cbddc2d31291c8f213ea3b97edafe0d/href To list an NFT, the owner must call the place_order function with Side == Sell.

 When the seller decides to accept a bid, they need to call the execute_order function with Side == Sell.

 However, the call to execute_order fails because the user is required to use the transfer function in Sway. This built-in function includes critical checks enforced by the FuelVM , one of which ensures that the caller possesses the specified asset_id and the required amount.

 https://medium.com/media/10d72b62807d7563ddab1be955da50bc/href This makes it impossible for the seller to accept any bids; they must either wait for someone to buy the NFT directly or cancel the order.

 As a result, sellers are unable to accept bid offers due to incorrect logic in the _execute_sell_taker_order function, which causes the transaction to revert when a bid is accepted.

### PoC and Exploit Steps:

 - Initialize all necessary contracts and configure them, including adding strategies and assets.

- The NFT owner places a sell order, transferring their NFT to the ThunderExchange contract.

- A bidder places a buy order targeting the same NFT but at a lower price.

- The NFT owner attempts to accept the buy order, but the execute_order function fails as the NFT is no longer in their possession.

- The PoC highlights a logic flaw that prevents NFT owners from accepting bids while their NFT is listed for sale.

 https://medium.com/media/fccdb5db7802ee34de21f1488fc290d5/href For more interesting bugs and writeups about web3 security, do check out our Medium as well as follow our X/Twitter to get daily updates!

 Top 3 Bugs from the ThunderNFT Invite Only Program was originally published in Immunefi on Medium, where people are continuing the conversation by highlighting and responding to this story.
