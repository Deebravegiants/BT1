# [M] The `owner` is a single point of failure and a centralization risk

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/365
Type: code-finding

## Details
### Lines of code

--------------

[56](https://github.com/Tapioca-DAO/YieldBox/blob/f5ad271b2dcab8b643b7cf622c2d6a128e109999/contracts/NativeTokenFactory.sol#L56-L56), [109](https://github.com/Tapioca-DAO/YieldBox/blob/f5ad271b2dcab8b643b7cf622c2d6a128e109999/contracts/NativeTokenFactory.sol#L109-L109), [127](https://github.com/Tapioca-DAO/YieldBox/blob/f5ad271b2dcab8b643b7cf622c2d6a128e109999/contracts/NativeTokenFactory.sol#L127-L127), [172](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/Balancer.sol#L172-L184), [219](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/Balancer.sol#L219-L224), [250](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/Balancer.sol#L250-L254), [115](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/TapiocaWrapper.sol#L115-L119), [131](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/TapiocaWrapper.sol#L131-L138), [154](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/TapiocaWrapper.sol#L154-L159), [116](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/mTapiocaOFT.sol#L116-L119), [131](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/mTapiocaOFT.sol#L131-L134), [130](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/Vesting.sol#L130-L130), [151](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/Vesting.sol#L151-L151), [455](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L455-L455), [308](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L308-L311), [318](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L318-L320), [324](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L324-L328), [344](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L344-L348), [357](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L357-L359), [365](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L365-L367), [446](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L446-L449), [458](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L458-L462), [471](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L471-L473), [479](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L479-L481), [259](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L259-L262), [276](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L276-L280), [297](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L297-L299), [326](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/BaseTapOFT.sol#L326-L326), [53](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L53-L53), [140](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L140-L142), [152](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L152-L152), [160](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L160-L160), [256](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L256-L256), [263](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L263-L263), [281](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L281-L281), [291](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L291-L291), [317](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L317-L320), [339](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L339-L342), [362](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L362-L372), [381](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L381-L384), [395](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L395-L405), [414](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L414-L417), [424](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L424-L433), [455](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L455-L455), [464](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L464-L464), [142](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/Market.sol#L142-L142), [151](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/Market.sol#L151-L151), [158](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/Market.sol#L158-L170), [442](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L442-L444), [466](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L466-L471), [477](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/Singularity.sol#L477-L479), [489](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/Singularity.sol#L489-L497), [576](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/Singularity.sol#L576-L580), [88](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L88-L88), [96](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L96-L96), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L105-L105), [125](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L125-L125), [134](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/BaseUSDO.sol#L134-L134), [61](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/UniswapV3Swapper.sol#L61-L61), [122](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/aave/AaveStrategy.sol#L122-L122), [129](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/aave/AaveStrategy.sol#L129-L129), [209](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/aave/AaveStrategy.sol#L209-L209), [109](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/balancer/BalancerStrategy.sol#L109-L109), [120](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/balancer/BalancerStrategy.sol#L120-L120), [89](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/compound/CompoundStrategy.sol#L89-L89), [100](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/compound/CompoundStrategy.sol#L100-L100), [148](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L148-L148), [163](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L163-L163), [170](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L170-L170), [179](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/convex/ConvexTricryptoStrategy.sol#L179-L179), [134](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoLPStrategy.sol#L134-L134), [141](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoLPStrategy.sol#L141-L141), [150](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoLPStrategy.sol#L150-L150), [199](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoLPStrategy.sol#L199-L199), [125](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L125-L125), [132](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L132-L132), [141](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L141-L141), [182](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L182-L182), [104](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L104-L104), [113](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/glp/GlpStrategy.sol#L113-L113), [93](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L93-L93), [104](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/lido/LidoEthStrategy.sol#L104-L104), [142](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L142-L142), [149](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L149-L149), [193](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L193-L193), [90](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L90-L90), [101](https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/yearn/YearnStrategy.sol#L101-L101)

### Vulnerability details

-------------

Having a single EOA as the only owner of contracts is a large centralization risk and a single point of failure. A single private key may be taken in a hack, or the sole holder of the key may become unable to retrieve the key when necessary, or the single owner can become malicious and perform a rug-pull. Consider changing to a multi-signature setup, and or having a role-based authorization model.

```solidity
File: contracts/NativeTokenFactory.sol

56:      function transferOwnership(uint256 tokenId, address newOwner, bool direct, bool renounce) public onlyOwner(tokenId) {

109:     function mint(uint256 tokenId, address to, uint256 amount) public onlyOwner(tokenId) {

127:     function batchMint(uint256 tokenId, address[] calldata tos, uint256[] calldata amounts) public onlyOwner(tokenId) {

```



```solidity
File: contracts/Balancer.sol

172      function rebalance(
173          address payable _srcOft,
174          uint16 _dstChainId,
175          uint256 _slippage,
176          uint256 _amount,
177          bytes memory _ercData
178      )
179          external
180          payable
181          onlyOwner
182          onlyValidDestination(_srcOft, _dstChainId)
183          onlyValidSlippage(_slippage)
184:     {

219      function initConnectedOFT(
220          address _srcOft,
221          uint16 _dstChainId,
222          address _dstOft,
223          bytes memory _ercData
224:     ) external onlyOwner {

250      function addRebalanceAmount(
251          address _srcOft,
252          uint16 _dstChainId,
253          uint256 _amount
254:     ) external onlyValidDestination(_srcOft, _dstChainId) onlyOwner {

```



```solidity
File: contracts/TapiocaWrapper.sol

115      function executeTOFT(
116          address _toft,
117          bytes calldata _bytecode,
118          bool _revertOnFailure
119:     ) external payable onlyOwner returns (bool success, bytes memory result) {

131      function executeCalls(
132          ExecutionCall[] calldata _call
133      )
134          external
135          payable
136          onlyOwner
137          returns (bool success, bytes[] memory results)
138:     {

154      function createTOFT(
155          address _erc20,
156          bytes calldata _bytecode,
157          bytes32 _salt,
158          bool _linked
159:     ) external onlyOwner {

```



```solidity
File: contracts/tOFT/mTapiocaOFT.sol

116      function updateConnectedChain(
117          uint256 _chain,
118          bool _status
119:     ) external onlyOwner {

131      function updateBalancerState(
132          address _balancer,
133          bool _status
134:     ) external onlyOwner {

```



```solidity
File: contracts/Vesting.sol

130:     function registerUser(address _user, uint256 _amount) external onlyOwner {

151:     function init(IERC20 _token, uint256 _seededAmount) external onlyOwner {

```



```solidity
File: contracts/governance/twTAP.sol

455:     function addRewardToken(IERC20 token) external onlyOwner returns (uint256) {

```



```solidity
File: contracts/option-airdrop/AirdropBroker.sol

308      function setTapOracle(
309          IOracle _tapOracle,
310          bytes calldata _tapOracleData
311:     ) external onlyOwner {

318      function setPhase2MerkleRoots(
319          bytes32[4] calldata _merkleRoots
320:     ) external onlyOwner {

324      function registerUserForPhase(
325          uint256 _phase,
326          address[] calldata _users,
327          uint256[] calldata _amounts
328:     ) external onlyOwner {

344      function setPaymentToken(
345          ERC20 _paymentToken,
346          IOracle _oracle,
347          bytes calldata _oracleData
348:     ) external onlyOwner {

357      function setPaymentTokenBeneficiary(
358          address _paymentTokenBeneficiary
359:     ) external onlyOwner {

365      function collectPaymentTokens(
366          address[] calldata _paymentTokens
367:     ) external onlyOwner {

```



```solidity
File: contracts/options/TapiocaOptionBroker.sol

446      function setTapOracle(
447          IOracle _tapOracle,
448          bytes calldata _tapOracleData
449:     ) external onlyOwner {

458      function setPaymentToken(
459          ERC20 _paymentToken,
460          IOracle _oracle,
461          bytes calldata _oracleData
462:     ) external onlyOwner {

471      function setPaymentTokenBeneficiary(
472          address _paymentTokenBeneficiary
473:     ) external onlyOwner {

479      function collectPaymentTokens(
480          address[] calldata _paymentTokens
481:     ) external onlyOwner {

```



```solidity
File: contracts/options/TapiocaOptionLiquidityProvision.sol

259      function setSGLPoolWEight(
260          IERC20 singularity,
261          uint256 weight
262:     ) external onlyOwner updateTotalSGLPoolWeights {

276      function registerSingularity(
277          IERC20 singularity,
278          uint256 assetID,
279          uint256 weight
280:     ) external onlyOwner updateTotalSGLPoolWeights {

297      function unregisterSingularity(
298          IERC20 singularity
299:     ) external onlyOwner updateTotalSGLPoolWeights {

```



```solidity
File: contracts/tokens/BaseTapOFT.sol

326:     function setTwTap(address _twTap) external onlyOwner {

```



```solidity
File: contracts/tokens/LTap.sol

53:      function setLockedUntil(uint256 _lockedUntil) external onlyOwner {

```



```solidity
File: contracts/tokens/TapOFT.sol

140      function setGovernanceChainIdentifier(
141          uint256 _identifier
142:     ) external onlyOwner {

152:     function updatePause(bool val) external onlyOwner {

160:     function setMinter(address _minter) external onlyOwner {

```



```solidity
File: contracts/Penrose.sol

256:     function setBigBangEthMarketDebtRate(uint256 _rate) external onlyOwner {

263:     function setBigBangEthMarket(address _market) external onlyOwner {

281:     function setConservator(address _conservator) external onlyOwner {

291:     function setUsdoToken(address _usdoToken) external onlyOwner {

317      function registerSingularityMasterContract(
318          address mcAddress,
319          IPenrose.ContractType contractType_
320:     ) external onlyOwner {

339      function registerBigBangMasterContract(
340          address mcAddress,
341          IPenrose.ContractType contractType_
342:     ) external onlyOwner {

362      function registerSingularity(
363          address mc,
364          bytes calldata data,
365          bool useCreate2
366      )
367          external
368          payable
369          onlyOwner
370          registeredSingularityMasterContract(mc)
371          returns (address _contract)
372:     {

381      function addSingularity(
382          address mc,
383          address _contract
384:     ) external onlyOwner registeredSingularityMasterContract(mc) {

395      function registerBigBang(
396          address mc,
397          bytes calldata data,
398          bool useCreate2
399      )
400          external
401          payable
402          onlyOwner
403          registeredBigBangMasterContract(mc)
404          returns (address _contract)
405:     {

414      function addBigBang(
415          address mc,
416          address _contract
417:     ) external onlyOwner registeredBigBangMasterContract(mc) {

424      function executeMarketFn(
425          address[] calldata mc,
426          bytes[] memory data,
427          bool forceSuccess
428      )
429          external
430          onlyOwner
431          notPaused
432          returns (bool[] memory success, bytes[] memory result)
433:     {

455:     function setFeeTo(address feeTo_) external onlyOwner {

464:     function setSwapper(ISwapper swapper, bool enable) external onlyOwner {

```



```solidity
File: contracts/markets/Market.sol

142:     function setBorrowOpeningFee(uint256 _val) external onlyOwner {

151:     function setBorrowCap(uint256 _cap) external notPaused onlyOwner {

158      function setMarketConfig(
159          uint256 _borrowOpeningFee,
160          IOracle _oracle,
161          bytes calldata _oracleData,
162          address _conservator,
163          uint256 _callerFee,
164          uint256 _protocolFee,
165          uint256 _liquidationBonusAmount,
166          uint256 _minLiquidatorReward,
167          uint256 _maxLiquidatorReward,
168          uint256 _totalBorrowCap,
169          uint256 _collateralizationRate
170:     ) external onlyOwner {

```



```solidity
File: contracts/markets/bigBang/BigBang.sol

442      function refreshPenroseFees(
443          address
444:     ) external onlyOwner notPaused returns (uint256 feeShares) {

466      function setBigBangConfig(
467          uint256 _minDebtRate,
468          uint256 _maxDebtRate,
469          uint256 _debtRateAgainstEthMarket,
470          uint256 _liquidationMultiplier
471:     ) external onlyOwner {

```



```solidity
File: contracts/markets/singularity/Singularity.sol

477      function refreshPenroseFees(
478          address feeTo
479:     ) external onlyOwner notPaused returns (uint256 feeShares) {

489      function setSingularityConfig(
490          uint256 _lqCollateralizationRate,
491          uint256 _liquidationMultiplier,
492          uint256 _minimumTargetUtilization,
493          uint256 _maximumTargetUtilization,
494          uint64 _minimumInterestPerSecond,
495          uint64 _maximumInterestPerSecond,
496          uint256 _interestElasticity
497:     ) external onlyOwner {

576      function setLiquidationQueueConfig(
577          ILiquidationQueue _liquidationQueue,
578          address _bidExecutionSwapper,
579          address _usdoSwapper
580:     ) external onlyOwner {

```



```solidity
File: contracts/usd0/BaseUSDO.sol

88:      function setMaxFlashMintable(uint256 _val) external onlyOwner {

96:      function setFlashMintFee(uint256 _val) external onlyOwner {

105:     function setConservator(address _conservator) external onlyOwner {

125:     function setMinterStatus(address _for, bool _status) external onlyOwner {

134:     function setBurnerStatus(address _for, bool _status) external onlyOwner {

```



```solidity
File: contracts/Swapper/UniswapV3Swapper.sol

61:      function setPoolFee(uint24 _newFee) external onlyOwner {

```



```solidity
File: contracts/aave/AaveStrategy.sol

122:     function setDepositThreshold(uint256 amount) external onlyOwner {

129:     function setMultiSwapper(address _swapper) external onlyOwner {

209:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/balancer/BalancerStrategy.sol

109:     function setDepositThreshold(uint256 amount) external onlyOwner {

120:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/compound/CompoundStrategy.sol

89:      function setDepositThreshold(uint256 amount) external onlyOwner {

100:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/convex/ConvexTricryptoStrategy.sol

148:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

163:     function setDepositThreshold(uint256 amount) external onlyOwner {

170:     function setMultiSwapper(address _swapper) external onlyOwner {

179:     function setTricryptoLPGetter(address _lpGetter) external onlyOwner {

```



```solidity
File: contracts/curve/TricryptoLPStrategy.sol

134:     function setDepositThreshold(uint256 amount) external onlyOwner {

141:     function setMultiSwapper(address _swapper) external onlyOwner {

150:     function setTricryptoLPGetter(address _lpGetter) external onlyOwner {

199:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/curve/TricryptoNativeStrategy.sol

125:     function setDepositThreshold(uint256 amount) external onlyOwner {

132:     function setMultiSwapper(address _swapper) external onlyOwner {

141:     function setTricryptoLPGetter(address _lpGetter) external onlyOwner {

182:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/glp/GlpStrategy.sol

104:     function harvestGmx(uint256 priceNum, uint256 priceDenom) public onlyOwner {

113:     function setFeeRecipient(address recipient) external onlyOwner {

```



```solidity
File: contracts/lido/LidoEthStrategy.sol

93:      function setDepositThreshold(uint256 amount) external onlyOwner {

104:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/stargate/StargateStrategy.sol

142:     function setDepositThreshold(uint256 amount) external onlyOwner {

149:     function setMultiSwapper(address _swapper) external onlyOwner {

193:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```



```solidity
File: contracts/yearn/YearnStrategy.sol

90:      function setDepositThreshold(uint256 amount) external onlyOwner {

101:     function emergencyWithdraw() external onlyOwner returns (uint256 result) {

```


### Assessed type

------------

other
