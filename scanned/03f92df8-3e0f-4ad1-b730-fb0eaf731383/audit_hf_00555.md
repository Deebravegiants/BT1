# [C] C-06 | Utilizing Vault Transfer To Steal Funds

## Summary
Severity: Critical
Contest weight: 0.3451
Dataset id: 2015
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Owner can transfer the ownership of the entire vault to any other address via transferFrom function
in ExitVaultEntryPoint contract. However this transfer only changes the owner of the NFT and owner
value in GmxAStorage struct, but does not update any other user related values (GMXStream and
GLPStream values).
This creates an important attack vector and also some unexpected scenarios because of the
ambiguity of the action. Firstly, ownerInitialGMX and ownerInitialGLP are variables that will be
transferred back to owner after a year exits. And owner can use ownership transfer mechanism to
increment these values and steal funds from other users.
Here is the attack path:
1. Transfer ownership to your second address.
2. createWithdrawRequest, so that when it is matched, your address won't be the owner anymore
and ownerInitialGmx won't be updated.
3. Transfer ownership back main address.
4. You sold your shares but still holding ownerInitialGmx and ownerInitialGlp which you can get
those amounts back when vesting ends.
Apart from this issue it is also not clear what this ownership transfer tries to achieve. For example,
when token distribution happens, Vested GMX distribution will go to the new owner because the
transfer is done directly to the s.owner, hence the part that is not donated will go to new owner, but
reward accumulation still happens to old owner because owners' reward related variables are not
updated.
Another thing is while the shares are not transferred, ownerInitialGMX/GLP will belong to new owner
now. So while it is not clear what new owner will receive from this ownership transfer, it will also
create an attack vector to steal funds from other users.

## Recommendation
During ownership transfer, update everything related to both old owner and new owner. This includes
claiming rewards for both parties before transfer, updating GMXStream and GLPStream alongside
with s.owner change.
