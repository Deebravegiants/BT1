# [C] Genes are overrideable

## Summary
Severity: Critical
Contest weight: 0.6760
Dataset id: 5258
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function gene() can be called any time to change the gene implementation. Furthermore child accounts can change their own genes at will. Hence there is no difference between a TBA leaving their gene unset and passing whichever implementation it prefers when minting, or setting a new gene before each invocation of mint.

## Proof of Concept
```solidity
Create a variant of KinoAccountGeneTester which returns false:
contract KinoAccountGeneTester2 is KinoAccountMinter {
    constructor(address _kimap) KinoAccountMinter(_kimap) {}
    function gene() public pure returns (bool) {
        return false;
    }
}
Write the following test, which is like testGene except it changes the gene of sub.os before mintint sub.sub.os:
function testGeneInheritance() public {
    KinoAccountGeneTester geneTestImpl = new KinoAccountGeneTester(address(kimap));
    KinoAccountGeneTester2 geneTestImpl2 = new KinoAccountGeneTester2(address(kimap));
    // mint .os
    (address dotOsTba,) = callMint(zeroTba, "os", kinoAccount);
    // set gene of .os
    IMech(dotOsTba).execute(
        address(kimap), 0, abi.encodeWithSelector(IKimap.gene.selector, address(geneTestImpl)), 0
    );
    // mint sub.os with kinoAccount, but gene should set it to geneTestImpl
    (address subTba,) = callMint(dotOsTba, "sub", kinoAccount);
    // delete gene of .sub
    IMech(subTba).execute(
        address(kimap), 0, abi.encodeWithSelector(IKimap.gene.selector, address(geneTestImpl2)), 0
    );
    (address sub2Tba,) = callMint(zeroTba, "sub2", kinoAccount);
    assertTrue(KinoAccountGeneTester(payable(subTba)).gene(), "sub.os tba's custom fn gene() should return true");
    // mint sub.sub.os with kinoAccount, should inherit gene from sub.os
    (address subSubTba,) = callMint(subTba, "sub", kinoAccount);
    assertFalse(KinoAccountGeneTester(payable(subSubTba)).gene(), "subsubgene tba's gene() should return true");
}
```
We see that sub.sub.os does not inherit the behavior set by .os.

## Recommendation
Make genes immutable. Once set, they cannot be changed.
