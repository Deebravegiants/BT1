# [M] 5.2.8 ownercan resetfeeBpsset byadminfor token gated drops

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** ERC721SeaDrop.sol#L233-L245, SeaDrop.sol#L860, SeaDrop.sol#L889-L
**Description:** Only theadmincan call updateTokenGatedDropFee to updatefeeBps. However, theownercan call
updateTokenGatedDrop(address seaDropImpl, address allowedNftToken, TokenGatedDropStage calldata drop-
Stage) twice after that to reset thefeeBpsto 0 for a drop.

1. Once withdropStage.maxTotalMintableByWalletequal to 0 to wipe out the storage on theSeaDropside.
2. Then with the sameallowedNftTokenaddress and the other desired parameters, which would retrieve the
    previously wiped out drop stage data (withfeeBpsequal to 0).
NOTE: This type of attack does not apply toupdatePublicDropandupdatePublicDropFeepair. SinceupdatePub-
licDropcannot remove or update thefeeBps. OnceupdatePublicDropFeeis called with a specificfeeBpsthat
value remains for thisERC721SeaDropcontract-related storage onSeaDrop(_publicDrops[msg.sender] = pub-
licDrop). And any number of consecutive calls toupdatePublicDropwith any parameters cannot change the
already setfeeBps.
**Recommendation:** Theadmins could monitor all the activities forupdateTokenGatedDropcalls even when the
same oldallowedNftTokenis used and make sure to set the fees after each call if it is not a removal kind.
**OpenSea:** We can re-work it so thatupdateTokenGatedDropFee"initializes" a tokenGatedDrop stage (all params
0 besidesfeeBpsandrestrictFeeRecipients), and a partner is free to then edit other params and delete the
stage, but not create a new one. I believe that would be a workaround for current issues.
Proposed workaround:
Administrator/OpenSea is the only authorized user that can "initialize" a TokenGatedDrop. Initializing a token-gated
drop sets all params to zero exceptmaxTotalMintableByWallet = 1(struct will not be stored if== 0),feeBps, and
restrictFeeRecipients = true. The parameterstartTime = 0means the stage will not be active, and cannot
be made active by OpenSea.
The Owner/Partner can then update the initialized TokenGatedDrop stage (potentially including delete, if so de-
sired, but it would need to be re-initialized with a fee by OpenSea).
