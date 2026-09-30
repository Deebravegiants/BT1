# [?] RocketNodeAPI deposit function exploit fix

## Summary
Severity: Unknown
Chain: Rocket Pool
Component: rocket-pool/rocketpool
Published: 2018-09-20
Source: https://github.com/rocket-pool/rocketpool/commit/361f7508c8c428c6e284a48e2527593e498054b9
Type: security-commit

## Details
RocketNodeAPI deposit function exploit fix

## Patch
### contracts/contract/api/RocketNodeAPI.sol
```diff
@@ -77,6 +77,13 @@ contract RocketNodeAPI is RocketBase {
     }
 
 
+    /// @dev Only passes if the node contract exists and is registered to the specified owner
+    modifier onlyValidNodeContract(address _nodeOwner, address _nodeContract) {
+        require(rocketStorage.getAddress(keccak256(abi.encodePacked("node.contract", _nodeOwner))) == _nodeContract, "Node contract is not valid.");
+        _;
+    }
+
+
     /// @dev Only passes if the supplied minipool duration is valid
     /// @param _durationID The ID that determines the minipool duration
     modifier onlyValidDuration(string _durationID) {
@@ -237,7 +244,7 @@ contract RocketNodeAPI is RocketBase {
 
     /// @dev Process a deposit into a nodes contract
     /// @param _nodeOwner  The address of the nodes owner
-    function deposit(address _nodeOwner) public onlyValidNodeOwner(_nodeOwner) returns(address[]) { 
+    function deposit(address _nodeOwner) public onlyValidNodeOwner(_nodeOwner) onlyValidNodeContract(_nodeOwner, msg.sender) returns(address[]) { 
         // Check the deposit is ready to go first
         if(getDepositIsValid(_nodeOwner)) {
             // Get the minipool settings contract
```
