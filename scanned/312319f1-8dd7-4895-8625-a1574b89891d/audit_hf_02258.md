# [M] Improved Follow Logic In InteractionLogic::follow()

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 12398
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the Lens Protocol allows the user to follow a certain profile (via LensHub::follow()). In the meantime, it also allows the owner of the profile to log out the profile by burning the NFT token that uniquely identifies the profile. While examining the current logic, we notice a specific design needs to be revisited.
To elaborate, we show below the related code snippet of the contracts. We notice the InteractionLogic::follow() function is called inside the LensHub::follow() function. In the InteractionLogic::follow() function, the following statements are executed to ensure that the followed profile does exist:
string memory handle = _profileById[profileIds[i]].handle (line 47) and if (bytes(handle).length == 0) revert Errors.TokenDoesNotExist() (line 48). However, when the profile is logged out with the calling of LensHub::burn(), the _profileById[profileIds[i]].handle is not cleared. That is to say, the user can still follow the burnt profile, which may not fit the realistic scenario.
```solidity
/// @inheritdoc ILensHub
function burn(uint256 profileId) external override whenNotPaused {
    if (msg.sender != ownerOf(profileId)) revert Errors.NotProfileOwner();
    _burn(profileId);
    bytes32 handleHash = keccak256(bytes(_profileById[profileId].handle));
    _profileIdByHandleHash[handleHash] = 0;
```
Public
/// ***************************************
/// ***** PROFILE INTERACTION FUNCTIONS *****
/// ***************************************
```solidity
/// @inheritdoc ILensHub
function follow(uint256[] calldata profileIds, bytes[] calldata datas) external override whenNotPaused
    InteractionLogic.follow(msg.sender, profileIds, datas, FOLLOW_NFT_IMPL, _profileById);
```
```solidity
function follow(
    address follower,
    uint256[] calldata profileIds,
    bytes[] calldata followModuleDatas,
    address followNFTImpl,
    mapping(uint256 => DataTypes.ProfileStruct) storage _profileById
) external {
    if (profileIds.length != followModuleDatas.length) revert Errors.ArrayMismatch();
    for (uint256 i = 0; i < profileIds.length; i++) {
        string memory handle = _profileById[profileIds[i]].handle;
        if (bytes(handle).length == 0) revert Errors.TokenDoesNotExist();
        address followModule = _profileById[profileIds[i]].followModule;
        address followNFT = _profileById[profileIds[i]].followNFT;
        if (followNFT == address(0)) {
            followNFT = Clones.clone(followNFTImpl);
            _profileById[profileIds[i]].followNFT = followNFT;
            bytes4 firstBytes = bytes4(bytes(handle));
            string memory followNFTName = string(abi.encodePacked(handle, Constants.FOLLOW_NFT_NAME_SUFFIX));
            string memory followNFTSymbol = string(abi.encodePacked(firstBytes, Constants.FOLLOW_NFT_SYMBOL_SUFFIX));
            IFollowNFT(followNFT).initialize(profileIds[i], followNFTName, followNFTSymbol);
            emit Events.FollowNFTDeployed(profileIds[i], followNFT, block.timestamp);
        }
        IFollowNFT(followNFT).mint(follower);
        if (followModule != address(0)) {
            IFollowModule(followModule).processFollow(follower, profileIds[i], followModuleDatas[i]);
        }
        emit Events.Followed(follower, profileIds, block.timestamp);
```
Public

## Recommendation
Prevent the user to follow the burnt profile.
