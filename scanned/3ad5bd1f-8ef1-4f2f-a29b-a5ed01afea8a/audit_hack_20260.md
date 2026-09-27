# [H] 5.1.1 An allowedsignercan sign mints with malicious parameters

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** SeaDrop.sol#L259-L266, SeaDrop.sol#L318-L
**Description:** An allowedsigner(SeaDrop.sol#L318-L319) can sign mints that have either:

- mintParams.feeBpsequal to 0.
- A customfeeRecipientwithmintParams.restrictFeeRecipientsequal tofalseto circumvent the check
    at SeaDrop.sol#L469.
And thus avoid the protocol fee being paid or allow the protocol fee to be sent to a desired address decided by the
signer.
Note that theERC721SeaDrop ownercan allow signers by callingERC721SeaDrop.updateSigner. Therefore, the
ownercan allow an address they control as asignerand sign mints that have either one of the above features.
**OpenSea:** This is correct; currently any signer would have ultimate control around the parameters of a mint, and
this should be understood by parties who wish to use a centralized signer, ie, self-hosted or in a legal agreement
with a marketplace
However, we could make it slightly less "trustful" by storing a struct of validation params rather than a simplebool
in the mapping
struct SignedMintParams {
uint80 minMintPrice;
uint24 maxMaxTotalMintableByWallet;
uint48 minStartTime;
uint48 maxEndTime;
uint40 maxMaxTokenSupplyForStage;
uint16 maxFeeBps;
}

and always assumerestrictFeeRecipients == true.
**Spearbit:** That could work. If this solution is implemented, all the instances ofmintParams.<FIELDS>would need
to be replaced by the stored (storage) parameters in this function.
Also, a question comes up as to who would have the authority to setSignedMintParamsbased on the current
architecture.
Is there a reason you didn't includedropStageIndexin theSignedMintParamsstruct?
In the aboveSignedMintParamsstruct, the last field is namedmaxFeeBps. Was that intentional or did you meant to
name itfeeBps?
**OpenSea** dropStageIndexis purely informational for metrics-purposes as part of theSeaDropMintevent (we want
to be able to see which addresses redeem allow-lists at which stage, etc)
In the case ofSignedMintParams, theOwnerwould set it, though for partnered drops, the fee-setting pattern would
likely be the same as elsewhere. (Pending confirmation from legal) OpenSea would initialize a signer with a
maxFeeBps (which still requires trust that we don't set it to a higher-than-agreed-upon value), and theOwnercan
then submit the rest of the parameters.
maxFeeBpswould allow variablefeeBps- which is probably a rare use-case, but was a requirement from product for
allow-list tiers, which we applied to the other mint methods. Enforcing amaxFeeBps, of course, includes the caveat
that it would not prevent a malicious signer from always specifying the maximum fee rate. The Owner should
specifymaxFeeBpsto ensure that a signer cannot specify afeeBpslarger than the largest acceptablefeeBps. (The
signer would be free to specify a lowerfeeBps, which I'm sure a creator would appreciate)


In the general case, if theOwnerchanges an allowed signer'smaxFeeBps(or any other mint parameter) to a value
that is no longer acceptable, the signer can refuse to sign mints.
