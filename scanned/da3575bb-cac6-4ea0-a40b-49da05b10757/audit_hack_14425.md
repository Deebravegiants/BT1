# [M] QA and other Gas Reports

## Summary
Severity: Medium
Reporter: boredpukar
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L101
Type: audit-issue

## Details
# QA and other Gas Reports

## Summary

QA and other Gas Reports

## Vulnerability Detail

As Below

## Impact

QA and other Gas Reports

## Low Issues

| |Issue|Instances|
|-|:-|:-:|
| [L-1](#L-1) | Do not rely on "block.timestamp". | 7 |
| [L-2](#L-2) | Do not use deprecated `_setupRole` library functions | 2 |
| [L-3](#L-3) | Solidity version 0.8.20 may not work on other chains due to `PUSH0` | 2 |
### <a name="L-1"></a>[L-1] Do not rely on "block.timestamp".

#### Impact:
Miners can influence the value of block.timestamp.

*Instances (7)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L101

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L139

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L191

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L192

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L193

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L196

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L199


```solidity
File: MertiDutchAction.sol

101:         return getPriceAt(block.timestamp);

139:         require(block.timestamp >= startTime, "Auction not started");

191:         if(block.timestamp < startTime) {

192:             timeToStart = startTime - block.timestamp;

193:         } else if(block.timestamp >= endTime) {

196:             uint256 timePassed = block.timestamp - startTime;

199:             timeToEnd = endTime - block.timestamp;

```

### <a name="L-2"></a>[L-2] Do not use deprecated `_setupRole` library functions
The function [_setupRole is deprecated](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.2/contracts/access/AccessControl.sol#L204-#L208) in favor of `_grantRole` function. The function may currently work, but if a bug is found in this version of OpenZeppelin, and the version that you're forced to upgrade to no longer has this function, you'll encounter unnecessary delays in porting and testing replacement contracts.

*Instances (2)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L53

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L54

```solidity
File: MeritNFT.sol

53:         _setupRole(URI_SETTER, _uriSetter);

54:         _setupRole(MINTER_ROLE, _minter);

```

### <a name="L-3"></a>[L-3] Solidity version 0.8.20 may not work on other chains due to `PUSH0`
The compiler for Solidity 0.8.20 switches the default target EVM version to [Shanghai](https://blog.soliditylang.org/2023/05/10/solidity-0.8.20-release-announcement/#important-note), which includes the new PUSH0 op code. This op code may not yet be implemented on all L2s, so deployment on these chains will fail. To work around this issue, use an [earlier EVM](https://docs.soliditylang.org/en/v0.8.20/using-the-compiler.html?ref=zaryabs.com#setting-the-evm-version-to-target) version

*Instances (2)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L2

```solidity
File: MeritNFT.sol

2: pragma solidity ^0.8.13;

```


Link to code: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L2

```solidity
File: MertiDutchAction.sol

2: pragma solidity ^0.8.13;

```


## Gas Optimizations


| |Issue|Instances|
|-|:-|:-:|
| [GAS-1](#GAS-1) | Cache the length of the array to avoid repeated computation thus saving gas (per iteration). | 1 |
| [GAS-2](#GAS-2) | State variables should be cached in stack variables rather than re-reading them from storage. | 3 |
| [GAS-3](#GAS-3) | Use calldata instead of memory for function arguments that do not get mutated. | 4 |
| [GAS-4](#GAS-4) | Use `!= 0` instead of `> 0` for unsigned integer comparison. | 2 |
| [GAS-5](#GAS-5) | Use custom errors instead of revert strings for gas savings. | 11 |
| [GAS-6](#GAS-6) | Don't initialize variables with default value. | 6 |
| [GAS-7](#GAS-7) | Pre-increments and pre-decrements are cheaper than post-increments and post-decrements. | 2 |
| [GAS-8](#GAS-8) | Functions guaranteed to revert when called by normal users can be marked `payable`. | 4 |
| [GAS-9](#GAS-9) | Constructor can be marked as payable to save gas. | 1 |
| [GAS-10](#GAS-10) | Using `private` rather than `public` for constants, saves gas. | 4 |
| [GAS-11](#GAS-11) | Use shorter revert strings. Also, use custom errors instead of revert strings for gas savings. | 3 |
| [GAS-12](#GAS-12) | For operations that will not overflow, you could use unchecked. | 19 |
### <a name="GAS-1"></a>[GAS-1] Cache the length of the array to avoid repeated computation thus saving gas (per iteration).
When the length of an array is read in each iteration of the loop using the .length property, it  triggers an SLOAD (storage read) operation. This can be expensive in terms of gas, especially if the array is large or the function is called many times. Additionally, the loop also increments the loop variable in each iteration, which is unnecessary.
If the length of the array is stored in a local variable before the loop starts, it reduces the number of SLOAD operations to just one. This improves the performance of the function and reduces the gas cost. Additionally, the loop variable is incremented only once per iteration, making the loop more efficient.

*Instances (1)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202

```solidity
File: MertiDutchAction.sol

202:         for(uint256 i = 0; i < priceSteps.length; i++) {

```

### <a name="GAS-2"></a>[GAS-2] State variables should be cached in stack variables rather than re-reading them from storage.
The instances below point to the second+ access of a state variable within a function. Caching of a state variable replaces each Gwarmaccess (100 gas) with a much cheaper stack read. Other less obvious fixes/optimizations include having local memory caches of state variable structs, or having local caches of state variable contracts/addresses.

*Saves 100 gas per instance*

*Instances (3)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L203

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L215

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L216

```solidity
File: MertiDutchAction.sol

203:             priceStepTimestamps[i] = startTime + i * stepSize;

215:             endTime: endTime,

216:             stepSize: stepSize,

```

### <a name="GAS-3"></a>[GAS-3] Use calldata instead of memory for function arguments that do not get mutated.
Mark data types as `calldata` instead of `memory` where possible. This makes it so that the data is not automatically loaded into memory. If the data passed into the function does not need to be changed (like updating values in an array), it can be passed in as `calldata`. The one exception to this is if the argument must later be passed into another function that takes an argument that specifies `memory` storage.

*Instances (4)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#46

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L47

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#48

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#67

```solidity
File: MeritNFT.sol

46:         string memory _name,

47:         string memory _symbol,

48:         string memory _baseTokenURI,

67:     function setBaseURI(string memory _newBaseURI) external onlyUriSetter {

```

### <a name="GAS-4"></a>[GAS-4] Use `!= 0` instead of `> 0` for unsigned integer comparison.
When dealing with unsigned integer types, comparisons with `!= 0` are cheaper than those with `> 0`

*Instances (2)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L101

```solidity
File: MeritNFT.sol

101:         return bytes(baseURI_).length > 0 ? string(abi.encodePacked(baseURI_, tokenId.toString(), ".json")) : "";

```


Link to code: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L76

```solidity
File: MertiDutchAction.sol

76:         require(stepSize_ > 0, "Step size must be greater than 0");

```

### <a name="GAS-5"></a>[GAS-5] Use custom errors instead of revert strings for gas savings.
Starting from Solidity version 0.8.4, there is a convenient and gas efficient way to explain why an operation failed through the use of custom errors. The require and revert strings are rather expensive, especially when it comes to deployment and runtime cost.
Custom errors are defined using the error statement, which can be used inside and outside of contracts, including interfaces and libraries. [Reference](https://blog.soliditylang.org/2021/04/21/custom-errors/)

*Instances (11)*:

Link to code: 

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L98

```solidity
File: MeritNFT.sol

98:         require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");

```


Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L76

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L93

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L139

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L141

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#143

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L145

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L164

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L176


```solidity
File: MertiDutchAction.sol

76:         require(stepSize_ > 0, "Step size must be greater than 0");

78:         require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");

80:         require(startPrice_ > endPrice_, "Start price must be greater than end price");

93:         require(address(nft) == address(0), "NFT already set");

139:         require(block.timestamp >= startTime, "Auction not started");

141:         require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");

143:         require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");

145:         require(msg.value >= totalPaid, "Insufficient funds");

164:             require(success, "Refund failed");

176:         require(success, "Claim failed");

```

### <a name="GAS-6"></a>[GAS-6] Don't initialize variables with default value.
If the variable is not initialized, it is assumed to have a default value. For example, 0 for a uint variable and false for a boolean variable. When we explicitly initialize it with its default value, we are simply wasting gas.

*Instances (6)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L186

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L187

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L188

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L189

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202

```solidity
File: MertiDutchAction.sol

156:         for(uint256 i = 0; i < amount; i++) {

186:         uint256 currentStep = 0;

187:         uint256 timeToNextStep = 0;

188:         uint256 timeToStart = 0;

189:         uint256 timeToEnd = 0;

202:         for(uint256 i = 0; i < priceSteps.length; i++) {

```

### <a name="GAS-7"></a>[GAS-7] Pre-increments and pre-decrements are cheaper than post-increments and post-decrements.
The majority of Solidity loops increment a uint256 variable that starts at 0. These increment operations never need to be checked for overflow or underflow because they will run out of gas, thus never reaching the max number of the uint256 value.
The operation has the tendency to save a decent amount of gas (30-40 gas) per loop iteration. However, for a lengthy loop, this value can be very significant.

*Instances (2)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L202

```solidity
File: MertiDutchAction.sol

156:         for(uint256 i = 0; i < amount; i++) {

202:         for(uint256 i = 0; i < priceSteps.length; i++) {

```

### <a name="GAS-8"></a>[GAS-8] Functions guaranteed to revert when called by normal users can be marked `payable`.
If a function modifier such as `onlyOwner` is used, the function will revert if a normal user tries to pay the function. Marking the function as `payable` will lower the gas cost for legitimate callers because the compiler will not include checks for whether a payment was provided.

*Instances (4)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L61

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L67

```solidity
File: MeritNFT.sol

61:     function mint(uint256 _tokenId, address _receiver) external onlyMinter {

67:     function setBaseURI(string memory _newBaseURI) external onlyUriSetter {

```


Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172

```solidity
File: MertiDutchAction.sol

91:     function setNFT(address nft_) external onlyOwner {

172:     function claimProceeds() external onlyOwner {

```

### <a name="GAS-9"></a>[GAS-9] Constructor can be marked as payable to save gas.
When a constructor is marked as payable, it means that it can receive Ether during contract deployment. By default, constructors are not payable, meaning they cannot receive any Ether.
When a constructor is not marked as payable, the Solidity compiler automatically generates a value check to ensure that no Ether is sent during deployment. This value check adds some bytecode and incurs gas costs during deployment.
However, when you mark the constructor as payable, the value check is not generated, and therefore, the associated gas costs are eliminated. This can result in some gas savings during contract deployment. It is important to note that marking the constructor as payable should only be done if you explicitly want to receive Ether during deployment and have a specific use case for it.

*Instances (1)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68

```solidity
File: MertiDutchAction.sol

68:     constructor(

```

### <a name="GAS-10"></a>[GAS-10] Using `private` rather than `public` for constants, saves gas.
If needed, the values can be read from the verified contract source code, or if there are multiple values there can be a single getter function that [returns a tuple](https://github.com/code-423n4/2022-08-frax/blob/90f55a9ce4e25bceed3a74290b854341d8de6afa/src/contracts/FraxlendPair.sol#L156-L178) of the values of all currently-public constants. Saves **3406-3606 gas** in deployment gas due to the compiler not having to create non-payable getter functions for deployment calldata, not having to store the bytes of the value outside of where it's used, and not adding another entry to the method ID table

*Instances (4)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L19

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L21

```solidity
File: MeritNFT.sol

19:     bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

21:     bytes32 public constant URI_SETTER = keccak256("URI_SETTER");

```


Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L14

```solidity
File: MertiDutchAction.sol

12:     uint256 constant public CAP_PER_ADDRESS = 4;

14:     uint256 constant public MINT_CAP = 10000;

```

### <a name="GAS-11"></a>[GAS-11] Use shorter revert strings. Also, use custom errors instead of revert strings for gas savings.
In Solidity, a string is a dynamic array of bytes. When a string is stored in memory, it is split into 32-byte-sized chunks, also known as "words," to make it easier for the Solidity compiler to work with. Each word can hold up to 32 bytes of data.
When a require statement fails, it causes the entire transaction to revert, which means that all the gas used by the transaction up to that point is lost. This includes the gas that was used to run the require statement and any other code in the transaction.
Using shorter revert strings reduces the amount of gas consumed by require statements, which can help reduce the cost of transactions for users. Shorter strings also help keep the bytecode size of the smart contract smaller, which can help reduce deployment costs and improve overall contract performance.
That being said, it is still important to provide enough context in the revert string to help users understand why the require statement failed. A good balance is to use short, descriptive error messages that convey the reason for the failure without being unnecessarily verbose. It is also a good practice to use error codes in the revert strings to help with automated error handling and debugging.
If smart contract supports Solidity 0.8.4 or higher, we might also consider using custom errors. Custom errors are cheaper (in terms of deployment and runtime cost) than revert strings when the revert statements are met.

*Instances (3)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L98

```solidity
File: MeritNFT.sol

98:         require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");

```


Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L80

```solidity
File: MertiDutchAction.sol

78:         require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");

80:         require(startPrice_ > endPrice_, "Start price must be greater than end price");

```

### <a name="GAS-12"></a>[GAS-12] For operations that will not overflow, you could use unchecked.

*Instances (19)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L137

```solidity
File: MertiDutchAction.sol

122:         uint256 price = startPrice - (priceRange * currentStep / totalSteps);

137:         uint256 totalPaid = pricePaid * amount;

141:         require(mintedBefore + amount <= MINT_CAP, "Mint cap reached");

143:         require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");

149:         minted += amount;

151:         mintedPerAddress[msg.sender] += amount;

153:         totalRaised += totalPaid;

156:         for(uint256 i = 0; i < amount; i++) {

156:         for(uint256 i = 0; i < amount; i++) {

158:             nft.mint(mintedBefore + i + 1, msg.sender);

158:             nft.mint(mintedBefore + i + 1, msg.sender);

184:         uint256[] memory priceSteps = new uint256[]((endTime - startTime) / stepSize + 1);

185:         uint256[] memory priceStepTimestamps = new uint256[]((endTime - startTime) / stepSize + 1);

198:             timeToNextStep = (currentStep + 1) * stepSize - timePassed;

198:             timeToNextStep = (currentStep + 1) * stepSize - timePassed;

202:         for(uint256 i = 0; i < priceSteps.length; i++) {

202:         for(uint256 i = 0; i < priceSteps.length; i++) {

203:             priceStepTimestamps[i] = startTime + i * stepSize;

203:             priceStepTimestamps[i] = startTime + i * stepSize;

```


## Non Critical Issues


| |Issue|Instances|
|-|:-|:-:|
| [NC-1](#NC-1) | Function name must be in mixedCase format. | 3 |
| [NC-2](#NC-2) | Private and internal variables must start with a single underscore. | 1 |
| [NC-3](#NC-3) | Event is missing `indexed` fields | 2 |
### <a name="NC-1"></a>[NC-1] Function name must be in mixedCase format.
Function name must be in mixedCase format.

*Instances (3)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L61

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L72

```solidity
File: MeritNFT.sol

61:     function mint(uint256 _tokenId, address _receiver) external onlyMinter {

72:     function _baseURI() internal view virtual override returns (string memory) {

```


Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

```solidity
File: MertiDutchAction.sol

128:     function mint(uint256 amount) external payable {

```

### <a name="NC-2"></a>[NC-2] Private and internal variables must start with a single underscore.

*Instances (1)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L23

```solidity
File: MeritNFT.sol

23:     string internal baseTokenURI_;

```

### <a name="NC-3"></a>[NC-3] Event is missing `indexed` fields
Index event fields make the field more quickly accessible to off-chain tools that parse events. However, note that each index field costs extra gas during emission, so it's not necessarily best to index the maximum allowed per event (three fields). Each event should use three indexed fields if there are three or more fields, and gas usage is not particularly of concern for the events in question. If there are fewer than three fields, all of the fields should be indexed.

*Instances (2)*:

Link to code:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L39

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L41

```solidity
File: MertiDutchAction.sol

39:     event Minted(address indexed to, uint256 amount, uint256 price);

41:     event ClaimedProceeds(uint256 amount);

```

## Tool used

Manual Review

## Recommendation

As suggested.
