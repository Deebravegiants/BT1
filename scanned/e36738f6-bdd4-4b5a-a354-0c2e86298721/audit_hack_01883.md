# [M] Only the `GOVERNANCE` can initialize the `Portal`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In the `Portal`'s `initialize` function, the `_GOVERNANCE` is passed as a parameter:


**code/contracts/Portal/Portal.sol:L156-L196**
```solidity
function initialize(
    address _GOVERNANCE,
    address _gETH,
    address _ORACLE_POSITION,
    address _DEFAULT_gETH_INTERFACE,
    address _DEFAULT_DWP,
    address _DEFAULT_LP_TOKEN,
    address _MINI_GOVERNANCE_POSITION,
    uint256 _GOVERNANCE_TAX,
    uint256 _COMET_TAX,
    uint256 _MAX_MAINTAINER_FEE,
    uint256 _BOOSTRAP_PERIOD
) public virtual override initializer {
    __ReentrancyGuard_init();
    __Pausable_init();
    __ERC1155Holder_init();
    __UUPSUpgradeable_init();

    GEODE.SENATE = _GOVERNANCE;
    GEODE.GOVERNANCE = _GOVERNANCE;
    GEODE.GOVERNANCE_TAX = _GOVERNANCE_TAX;
    GEODE.MAX_GOVERNANCE_TAX = _GOVERNANCE_TAX;
    GEODE.SENATE_EXPIRY = type(uint256).max;

    STAKEPOOL.GOVERNANCE = _GOVERNANCE;
    STAKEPOOL.gETH = IgETH(_gETH);
    STAKEPOOL.TELESCOPE.gETH = IgETH(_gETH);
    STAKEPOOL.TELESCOPE.ORACLE_POSITION = _ORACLE_POSITION;
    STAKEPOOL.TELESCOPE.MONOPOLY_THRESHOLD = 20000;

    updateStakingParams(
        _DEFAULT_gETH_INTERFACE,
        _DEFAULT_DWP,
        _DEFAULT_LP_TOKEN,
        _MAX_MAINTAINER_FEE,
        _BOOSTRAP_PERIOD,
        type(uint256).max,
        type(uint256).max,
        _COMET_TAX,
        3 days
    );
```

But then it calls the `updateStakingParams` function, which requires the `msg.sender` to be the governance:


**code/contracts/Portal/Portal.sol:L651-L665**
```solidity
function updateStakingParams(
    address _DEFAULT_gETH_INTERFACE,
    address _DEFAULT_DWP,
    address _DEFAULT_LP_TOKEN,
    uint256 _MAX_MAINTAINER_FEE,
    uint256 _BOOSTRAP_PERIOD,
    uint256 _PERIOD_PRICE_INCREASE_LIMIT,
    uint256 _PERIOD_PRICE_DECREASE_LIMIT,
    uint256 _COMET_TAX,
    uint256 _BOOST_SWITCH_LATENCY
) public virtual override {
    require(
        msg.sender == GEODE.GOVERNANCE,
        "Portal: sender not GOVERNANCE"
    );
```

So only the future governance can initialize the `Portal`. In the case of the Geode protocol, the governance will be represented by a token contract, making it hard to initialize promptly.  Initialization should be done by an actor that is more flexible than governance.


#### Recommendation

Split the `updateStakingParams` function into public and private ones and use them accordingly.
