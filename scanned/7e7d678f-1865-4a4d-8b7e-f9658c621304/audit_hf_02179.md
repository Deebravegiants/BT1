# [H] Improper Logic of ERC721Base::_addTokenTo()/_removeTokenFrom()

## Summary
Severity: High
Contest weight: 0.8997
Dataset id: 12159
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC721Base contract implements the standard ERC721 interfaces. Additionally, it implements the enumerability of all token IDs owned by the user.
In particular, mapping(address => uint256[]) internal _userTokens is designed to record all the token IDs held by the user and mapping(uint256 => uint256) internal _indexOfToken records the index of the token inside the user's token array. Meanwhile, the _addTokenTo() and _removeTokenFrom() routines are designed to manage the token IDs held by the user. While examining the related logic, we observe the current implementation should be improved.
To elaborate, we show below the related code snippet of the ERC721Base contract. Inside the _addTokenTo() routine, the statement of _userTokens[_to].push(_tokenId) (line 407) is executed to push the _tokenId to the _to's token array. Subsequently, the statement of _indexOfToken[_tokenId] = _userTokens[_to].length (line 408) is executed to record the index of the _tokenId inside the user's token array. However, it ignores the fact that the index of the array starts from 0.
```solidity
function _addTokenTo(address _to, uint256 _tokenId) internal {
    _tokenOwner[_tokenId] = _to;
    _userTokens[_to].push(_tokenId);
    _indexOfToken[_tokenId] = _userTokens[_to].length;
    _tokensCount = _tokensCount.add(1);
    _userPurchaseDate[_to] = block.timestamp;
}
```
Moreover, by design, the _removeTokenFrom() routine is used to remove the given _tokenId token from the given _from address. In order to meet the requirement, it needs to replace _tokenId with the last token ID inside the _from's token array and update the index of the last token ID. Eventually, the array's last element should be released via pop(). However, it comes to our attention that the current implementation is far from the design.
```solidity
function _removeTokenFrom(address _from, uint256 _tokenId) internal {
    uint256 tokenIndex = _indexOfToken[_tokenId];
    uint256 lastTokenIndex = _userTokens[_from].length.sub(1);
    uint256 lastTokenId = _indexOfToken[lastTokenIndex];
    _userTokens[_from][tokenIndex] = lastTokenId;
    _indexOfToken[lastTokenId] = tokenIndex;
    _userTokens[_from].pop();
    _tokenOwner[_tokenId] = address(0);
    _tokensCount = _tokensCount.sub(1);
    if (_userTokens[_from].length == 0) {
        delete _userTokens[_from];
    }
}
```

## Recommendation
Correct the implementation of above-mentioned routines as below:
```solidity
function _addTokenTo(address _to, uint256 _tokenId) internal {
    _tokenOwner[_tokenId] = _to;
    _userTokens[_to].push(_tokenId);
    _indexOfToken[_tokenId] = _userTokens[_to].length - 1;
    _tokensCount = _tokensCount.add(1);
    _userPurchaseDate[_to] = block.timestamp;
}

function _removeTokenFrom(address _from, uint256 _tokenId) internal {
    uint256 tokenIndex = _indexOfToken[_tokenId];
    uint256 lastTokenId = _userTokens[_from][_userTokens[_from].length - 1];
    _userTokens[_from][tokenIndex] = lastTokenId;
    delete _indexOfToken[_tokenId];
    _userTokens[_from].pop();
    _tokenOwner[_tokenId] = address(0);
    _tokensCount = _tokensCount.sub(1);
    if (_userTokens[_from].length == 0) {
        delete _userTokens[_from];
    }
}
```
